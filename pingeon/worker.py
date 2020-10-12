import asyncio
import logging
from functools import wraps
from typing import Awaitable, Callable, Coroutine, Union

from .utils import timer

logger = logging.getLogger(__name__)
Worker = Callable[[], Awaitable[None]]


def worker(
    sentinel: asyncio.Future, func: Worker, interval: Union[int, float]
) -> Coroutine:
    """
    Runs given func every given interval.

    :param sentinel: Use a future to stop worker
    :param func: Async function
    :param interval: Run interval in seconds
    :return:
    """

    @wraps(func)
    async def inner():
        with timer() as time:
            try:
                # todo: shield task for graceful shutdown
                await func()
            except asyncio.CancelledError:
                # todo: drop on 3.8
                return
            except Exception:
                logger.exception(f'"{func!r}" is failed')

        if sentinel.done():
            return

        # Recursive call
        loop = asyncio.get_event_loop()
        loop.call_later(
            max(0.0, interval - time.total),
            loop.create_task,
            inner(),
        )

    return inner()
