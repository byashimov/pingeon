from functools import partial
from itertools import count

import pytest
from asynctest import Mock, call

from pingeon import worker

pytestmark = pytest.mark.asyncio


async def test_worker(event_loop):
    logger = Mock()
    counter = count()
    sentinel = event_loop.create_future()

    async def my_worker(msg: str):
        value = next(counter)
        logger.debug(msg % value)
        if value:
            sentinel.set_result(None)
            logger.info("Shutting down")

    await worker(sentinel, partial(my_worker, "wow %d!"), 0.1)
    await sentinel

    # Regular task called twice
    assert logger.debug.call_count == 2
    logger.debug.assert_has_calls([call("wow 0!"), call("wow 1!")])

    # And once shutted down
    logger.info.assert_called_once_with("Shutting down")
