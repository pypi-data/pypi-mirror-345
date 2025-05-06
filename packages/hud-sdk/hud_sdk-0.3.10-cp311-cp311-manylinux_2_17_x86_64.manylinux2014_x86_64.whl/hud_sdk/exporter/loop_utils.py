import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

ReturnType = TypeVar("ReturnType")

thread_pool_executor = ThreadPoolExecutor(max_workers=10)


async def run_in_thread(
    loop: asyncio.AbstractEventLoop, fn: Callable[..., ReturnType], *args: Any
) -> ReturnType:
    return await loop.run_in_executor(thread_pool_executor, fn, *args)
