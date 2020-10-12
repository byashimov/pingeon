import asyncio
import logging
from functools import wraps
from typing import Awaitable, Callable, Coroutine, Union

from .utils import timer

logger = logging.getLogger(__name__)
Worker = Callable[..., Awaitable[None]]


def worker(func: Worker, interval: Union[int, float]) -> Coroutine:
    """
    Runs given func every interval in seconds
    """

    @wraps(func)
    async def inner(*args, **kwargs):
        with timer() as time:
            try:
                # todo: shield task for graceful shutdown
                await func(*args, **kwargs)
            except asyncio.CancelledError:
                # todo: drop on 3.8
                return
            except Exception:
                logger.exception(f'"{func.__name__}" is failed')

        # Recursive call
        loop = asyncio.get_event_loop()
        loop.call_later(
            max(0.0, interval - time.total),
            loop.create_task,
            inner(*args, **kwargs),
        )

    return inner()
