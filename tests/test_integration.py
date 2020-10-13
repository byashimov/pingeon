import asyncio
from functools import partial

import pytest

from pingeon import (
    KafkaConsumer,
    KafkaProducer,
    Postgres,
    consumer,
    producer,
    site_check,
    worker,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.skip(reason="Not ready yet")
async def test_integration(event_loop):
    """
    This test is mostly looks like a main() program.
    """

    sentinel = event_loop.create_future()
    postgres = Postgres()

    # This DDL should not be run by the code
    # Cause we don't want project postgres user make DDLs
    async with postgres:
        # todo: partition table by id interval
        await postgres.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id          SERIAL PRIMARY KEY,
                uid         TEXT UNIQUE,
                label       TEXT NOT NULL,
                status      TEXT NOT NULL,
                start_time  TIMESTAMP NOT NULL,
                end_time    TIMESTAMP NOT NULL,
                result      JSONB NOT NULL
            )
            """
        )

    # Creates Consumer.
    # Must clojure clients to make it be runnable by worker
    consume = partial(
        consumer,
        KafkaConsumer("test", group_id="test"),
        postgres,
    )

    # Creates Producer.
    # Must clojure clients and checkers
    check_example = partial(site_check, "http://example.com", "Example Domain")
    produce = partial(
        producer,
        KafkaProducer("test"),
        {"site_check": check_example},
    )

    # Workers are recursive tasks
    workers = event_loop.create_task(
        asyncio.gather(
            worker(sentinel, consume, 1),
            worker(sentinel, produce, 1),
        )
    )

    # Stops the test
    event_loop.call_later(3, sentinel.set_result, None)
    event_loop.call_later(5, workers.cancel, None)
