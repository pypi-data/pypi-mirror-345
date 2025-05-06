import asyncio
import time
from typing import Any, Callable, Coroutine, Optional, Set, Union  # noqa: F401

from ..config import config
from ..logging import internal_logger
from ..utils import suppress_exceptions_async


def _create_task(
    function: Callable[..., Coroutine[Any, Any, None]],
    *args: Any,
    **kwargs: Any,
) -> "asyncio.Task[Any]":
    coroutine = suppress_exceptions_async(lambda: None)(function)(*args, **kwargs)

    if hasattr(asyncio, "create_task"):
        task = asyncio.create_task(coroutine)
    else:
        loop = asyncio.get_event_loop()
        task = loop.create_task(coroutine)

    return task


class TaskManager:
    def __init__(self) -> None:
        self._tasks = set()  # type: Set[asyncio.Task[Any]]
        self._stop_event = asyncio.Event()
        self._complete_event = asyncio.Event()

    def _on_task_done(self, task: "asyncio.Task[Any]") -> None:
        self._tasks.discard(task)
        if not self._tasks:
            self._complete_event.set()

    async def _create_periodic_task(
        self,
        function: Union[Callable[..., Coroutine[Any, Any, None]], Callable[..., None]],
        interval: Union[float, Callable[[], float]],
        *args: Any,
        callback: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        # Wait for the first interval before running the function
        try:
            current_interval = interval() if callable(interval) else interval
            await asyncio.wait_for(self._stop_event.wait(), timeout=current_interval)
        except (asyncio.TimeoutError, TimeoutError):
            pass

        while not self._stop_event.is_set():
            current_interval = interval() if callable(interval) else interval
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(function):
                    await function(*args, **kwargs)
                else:
                    function(*args, **kwargs)
            except Exception:
                internal_logger.exception("Exception in periodic task")
            elapsed_time = time.time() - start_time
            if elapsed_time > current_interval or elapsed_time > 1:
                internal_logger.debug(
                    "long running periodic task",
                    data={
                        "interval": current_interval,
                        "func": str(function),
                        "elapsed": elapsed_time,
                    },
                )
            sleep_time = max(0.0001, current_interval - elapsed_time)
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=sleep_time)
            except (asyncio.TimeoutError, TimeoutError):
                pass
        if callback:
            try:
                await callback(*args, **kwargs)
            except Exception:
                internal_logger.exception("Exception in periodic task callback")

    def register_periodic_task(
        self,
        function: Union[Callable[..., Coroutine[Any, Any, None]], Callable[..., None]],
        interval: Union[float, Callable[[], float]],
        *args: Any,
        callback: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None,
        **kwargs: Any,
    ) -> "asyncio.Task[Any]":
        return self.register_task(
            self._create_periodic_task,
            function,
            interval,
            *args,
            callback=callback,
            **kwargs,
        )

    def register_task(
        self,
        function: Callable[..., Coroutine[Any, Any, None]],
        *args: Any,
        **kwargs: Any,
    ) -> "asyncio.Task[Any]":
        task = _create_task(function, *args, **kwargs)
        task.add_done_callback(self._on_task_done)
        self._tasks.add(task)
        return task

    def stop_running_tasks(self) -> None:
        _create_task(
            asyncio.sleep, config.exporter_stop_running_tasks_grace
        ).add_done_callback(lambda _task: self._complete_event.set())
        self._stop_event.set()

    async def wait_for_tasks(self) -> None:
        try:
            await self._complete_event.wait()
        finally:
            for task in self._tasks.copy():
                task.cancel()
