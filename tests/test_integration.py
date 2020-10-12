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
    sentinel = event_loop.create_future()
    postgres = Postgres()

    async with postgres:
        await postgres.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                label TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                result JSONB NOT NULL 
            ) PARTITION BY RANGE (start_time::date)
        """
        )

    consume = partial(
        consumer,
        KafkaConsumer("test", group_id="test"),
        postgres,
    )

    check_example = partial(site_check, "http://example.com", "Example Domain")
    produce = partial(
        producer,
        KafkaProducer("test"),
        {"site_check": check_example},
    )

    workers = event_loop.create_task(
        asyncio.gather(
            worker(sentinel, consume, 1),
            worker(sentinel, produce, 1),
        )
    )

    event_loop.call_later(3, sentinel.set_result, None)
    event_loop.call_later(5, workers.cancel, None)
