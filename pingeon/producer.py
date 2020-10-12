import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List

from .repositories import KafkaProducer

logger = logging.getLogger(__name__)
Checker = Callable[[], Awaitable[Dict[str, Any]]]


async def producer(kafka: KafkaProducer, checkers: List[Checker]):
    results = await asyncio.gather(
        *[c() for c in checkers],
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
