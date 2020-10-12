from functools import wraps
from typing import Any, Awaitable, Callable, Dict

from ..models import Log, Status
from ..utils import utcnow

Checker = Callable[..., Awaitable[Dict[str, Any]]]


async def checker(func: Checker) -> Checker:
    @wraps(func)
    async def inner(*args, **kwargs):
        start_time = utcnow()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            status = Status.FAILED
            result = {"error": repr(e)}
        else:
            status = Status.SUCCESS
        finally:
            end_time = utcnow()

        return Log(
            function=func.__name__,
            status=status,
            start_time=start_time,
            end_time=end_time,
            result=result,
        )

    return inner
