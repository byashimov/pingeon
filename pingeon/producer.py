import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List

from .checkers import CheckError
from .models import Log, Status
from .repositories import KafkaProducer
from .utils import utcnow

logger = logging.getLogger(__name__)
Checker = Callable[[], Awaitable[Dict[str, Any]]]


async def producer(kafka: KafkaProducer, checkers: List[Checker]):
    results = await asyncio.gather(
        *[check(c) for c in checkers],
        # Isolates checkers exceptions
        return_exceptions=True,
    )

    async with kafka:
        for item in results:
            if isinstance(item, Exception):
                # Logs failed tasks
                logger.exception(item)
            else:
                await kafka.send(item)


async def check(func: Checker) -> Log:
    start_time = utcnow()
    try:
        result = await func()
    except CheckError as e:
        status = Status.ERROR
        result = {"error": repr(e)}
    except Exception as e:
        # Check not failed, but check is failed O_o
        status = Status.FATAL
        result = {"error": repr(e)}
    else:
        status = Status.OK
    finally:
        end_time = utcnow()

    return Log(
        function=func.__name__,
        status=status,
        start_time=start_time,
        end_time=end_time,
        result=result,
    )
