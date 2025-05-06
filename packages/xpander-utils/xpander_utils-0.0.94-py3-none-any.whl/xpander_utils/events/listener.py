from __future__ import annotations

import asyncio
import json
import signal
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable, Callable, Optional, Set, Union

import httpx
from aiosseclient import aiosseclient
from loguru import logger
from xpander_sdk import XpanderClient  # type: ignore

from .git_init import configure_git_credentials
from .models.deployments import DeployedAsset
from .models.events import EventType, WorkerFinishedEvent, WorkerHeartbeat
from .models.executions import (
    AgentExecution,
    AgentExecutionResult,
    AgentExecutionStatus,
)

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #

EVENT_STREAMING_ENDPOINT = "{base}/{organization_id}/events"
ExecutionRequestHandler = Union[
    Callable[[AgentExecution], AgentExecutionResult],
    Callable[[AgentExecution], Awaitable[AgentExecutionResult]],
]

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


def _should_pass_org_id(base_url: Optional[str]) -> bool:
    if base_url is None:
        return False
    return not ("inbound.stg" in base_url or "inbound.xpander" in base_url)


# --------------------------------------------------------------------------- #
# Main class                                                                  #
# --------------------------------------------------------------------------- #


class XpanderEventListener:
    # --------------------------------------------------------------------- #
    # Construction                                                          #
    # --------------------------------------------------------------------- #

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        *,
        base_url: Optional[str] = None,
        organization_id: Optional[str] = None,
        should_reset_cache: bool = False,
        with_metrics_report: bool = False,
        max_sync_workers: int = 4,
    ) -> None:
        """
        Parameters
        ----------
        api_key
            Xpander API key.
        agent_id
            The agent whose events we listen to.
        base_url
            Override xpander.ai API base-URL (useful for staging / local).
        organization_id
            Organisation ID header (ignored for inbound URLs).
        should_reset_cache
            Forwarded to :class:`xpander_sdk.XpanderClient`.
        with_metrics_report
            Enable automatic LLM/execution metrics.
        max_sync_workers
            Size of the internal :class:`ThreadPoolExecutor` for sync handlers.
        """
        configure_git_credentials()

        xpander_client = XpanderClient(
            api_key=api_key,
            base_url=base_url,
            organization_id=organization_id if _should_pass_org_id(base_url) else None,
            should_reset_cache=should_reset_cache,
        )

        # Public attributes
        self.api_key = api_key
        self.agents = [agent_id]
        self.organization_id = organization_id
        self.base_url = xpander_client.configuration.base_url.rstrip("/")
        self.with_metrics_report = with_metrics_report

        # Internal resources
        self._pool: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=max_sync_workers,
            thread_name_prefix="xpander-handler",
        )
        self._bg: Set[asyncio.Task] = set()
        self._root_worker: DeployedAsset | None = None

        logger.debug(
            f"XpanderEventListener initialised (base_url={self.base_url}, "
            f"org_id={self.organization_id})"
        )

    # --------------------------------------------------------------------- #
    # Public lifecycle                                                      #
    # --------------------------------------------------------------------- #

    async def start(
        self,
        on_execution_request: ExecutionRequestHandler,
    ) -> None:
        """
        Start listening indefinitely (until cancelled or SIGINT/SIGTERM).

        **Typical async usage**

        ```python
        async def handler(exec_: AgentExecution) -> AgentExecutionResult:
            ...

        listener = XpanderEventListener(...)
        await listener.start(handler)          # inside an existing event-loop
        ```

        For synchronous code, see :pymeth:`register`.
        """
        loop = asyncio.get_running_loop()

        # Graceful Ctrl-C / docker-stop / systemctl-stop
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self.stop(s)))

        # Register root worker (blocks until first WorkerRegistration event)
        self._root_worker = await self._register_parent_worker()

        # One SSE consumer task per agent
        for agent_id in self.agents:
            self._track(
                asyncio.create_task(
                    self._register_agent_worker(agent_id, on_execution_request)
                )
            )

        logger.info("Listener started; waiting for events…")
        await asyncio.gather(*self._bg)  # run forever (or until cancelled)

    async def stop(self, sig: signal.Signals | None = None) -> None:
        """
        Cancel background tasks and shut down the thread-pool.

        Called automatically on SIGINT/SIGTERM but can also be invoked manually.
        """
        if sig:
            logger.info(f"Received {sig.name} – shutting down…")

        for t in self._bg:
            t.cancel()
        if self._bg:
            await asyncio.gather(*self._bg, return_exceptions=True)

        self._pool.shutdown(wait=False, cancel_futures=True)
        self._bg.clear()
        logger.info("Listener stopped.")

    # Pythonic context-manager sugar
    async def __aenter__(self) -> "XpanderEventListener":
        return self

    async def __aexit__(self, *_exc) -> bool:  # noqa: D401
        await self.stop()
        return False

    # --------------------------------------------------------------------- #
    # Internal helpers – networking                                         #
    # --------------------------------------------------------------------- #

    def _is_not_inbound(self) -> bool:
        return "inbound.xpander" not in self.base_url and "inbound.stg.xpander" not in self.base_url

    def _events_base(self) -> str:
        if self._is_not_inbound():
            return EVENT_STREAMING_ENDPOINT.format(
                base=self.base_url,
                organization_id=self.organization_id,
            )

        is_stg = "stg.xpander" in self.base_url
        base = f"https://agent-controller{'.stg' if is_stg else ''}.xpander.ai"
        return EVENT_STREAMING_ENDPOINT.format(base=base, organization_id=self.organization_id)

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self.api_key}

    async def _release_worker(self, worker_id: str) -> None:
        url = f"{self._events_base()}/{worker_id}"
        async with httpx.AsyncClient() as client:
            await client.post(
                url,
                headers=self._headers(),
                json=WorkerFinishedEvent().model_dump_safe(),
                follow_redirects=True,
            )

    async def _make_heartbeat(self, worker_id: str) -> None:
        url = f"{self._events_base()}/{worker_id}"
        async with httpx.AsyncClient() as client:
            await client.post(
                url,
                headers=self._headers(),
                json=WorkerHeartbeat().model_dump_safe(),
                follow_redirects=True,
            )

    async def _update_execution_result(
        self,
        execution_id: str,
        execution_result: AgentExecutionResult,
    ) -> None:
        base = self._events_base().replace("/events", "/agent-execution")
        url = f"{base}/{execution_id}/finish"

        async with httpx.AsyncClient() as client:
            await client.patch(
                url,
                headers=self._headers(),
                json={
                    "result": execution_result.result,
                    "status": (
                        AgentExecutionStatus.Completed
                        if execution_result.is_success
                        else AgentExecutionStatus.Error
                    ),
                },
                follow_redirects=True,
            )

    async def _mark_execution_as_executing(self, execution_id: str) -> None:
        base = self._events_base().replace("/events", "/agent-execution")
        url = f"{base}/{execution_id}/finish"

        async with httpx.AsyncClient() as client:
            await client.patch(
                url,
                headers=self._headers(),
                json={
                    "result": "",
                    "status": AgentExecutionStatus.Executing.value.lower(),
                },
                follow_redirects=True,
            )

    # --------------------------------------------------------------------- #
    # Internal helpers – execution path                                     #
    # --------------------------------------------------------------------- #

    async def _handle_agent_execution(
        self,
        agent_worker: DeployedAsset,
        execution_task: AgentExecution,
        on_execution_request: ExecutionRequestHandler,
    ) -> None:
        result = AgentExecutionResult(result="")
        try:
            await self._mark_execution_as_executing(execution_task.id)

            if asyncio.iscoroutinefunction(on_execution_request):
                result = await on_execution_request(execution_task)
            else:
                result = await asyncio.get_running_loop().run_in_executor(
                    self._pool,
                    on_execution_request,
                    execution_task,
                )
        except Exception as exc:
            logger.exception("Execution handler failed")
            result.is_success = False
            result.result = f"Error: {exc}"
        finally:
            await self._release_worker(agent_worker.id)
            await self._update_execution_result(execution_task.id, result)

    async def _register_agent_worker(
        self,
        agent_id: str,
        on_execution_request: ExecutionRequestHandler,
    ) -> None:
        assert self._root_worker, "Root worker must be registered first"
        url = f"{self._events_base()}/{self._root_worker.id}/{agent_id}"

        async for event in aiosseclient(url=url, headers=self._headers(), raise_for_status=True):
            if event.event == EventType.WorkerRegistration:
                agent_worker = DeployedAsset(**json.loads(event.data))
                logger.info(f"Worker registered – id={agent_worker.id}")

                # pretty chat URL for convenience
                agent_meta = agent_worker.metadata or {}
                if agent_meta:
                    is_stg = "stg." in self._events_base() or "localhost" in self._events_base()
                    chat_url = f"https://{agent_meta.get('unique_name', agent_id)}.agents"
                    chat_url += ".stg" if is_stg else ""
                    chat_url += ".xpander.ai"
                    logger.info(
                        f"Agent '{agent_meta.get('name', agent_id)}' chat: {chat_url}"
                    )

                self._track(asyncio.create_task(self._heartbeat_loop(agent_worker.id)))

            elif event.event == EventType.AgentExecution:
                exec_task = AgentExecution(**json.loads(event.data))
                self._track(
                    asyncio.create_task(
                        self._handle_agent_execution(
                            agent_worker, exec_task, on_execution_request
                        )
                    )
                )

    async def _register_parent_worker(self) -> DeployedAsset:
        url = self._events_base()

        async for event in aiosseclient(url=url, headers=self._headers(), raise_for_status=True):
            if event.event == EventType.WorkerRegistration:
                root = DeployedAsset(**json.loads(event.data))
                return root

        raise RuntimeError("Failed to register root worker – no WorkerRegistration received")

    # --------------------------------------------------------------------- #
    # Internal helpers – misc                                               #
    # --------------------------------------------------------------------- #

    def _track(self, task: asyncio.Task) -> None:
        """Add *task* to the background set and auto-remove on completion."""
        self._bg.add(task)
        task.add_done_callback(self._bg.discard)

    async def _heartbeat_loop(self, worker_id: str) -> None:
        while True:
            try:
                await self._make_heartbeat(worker_id)
            except Exception as exc:
                logger.error(f"Heartbeat for {worker_id} failed: {exc}")
            await asyncio.sleep(2)

    # --------------------------------------------------------------------- #
    # Synchronous convenience wrapper                                       #
    # --------------------------------------------------------------------- #

    def register(self, on_execution_request: ExecutionRequestHandler) -> None:
        """
        Start the listener in environments **without** an existing event-loop.

        This helper spins up an internal loop via :func:`asyncio.run` and blocks
        the current thread until the listener is stopped (e.g. with *Ctrl-C*).

        **Example**

        ```python
        def blocking_main():
            listener = XpanderEventListener(api_key=..., agent_id=...)
            listener.register(my_handler)
        ```

        For fully-async applications prefer calling :pymeth:`start` directly.
        """
        asyncio.run(self.start(on_execution_request))
