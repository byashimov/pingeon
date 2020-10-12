import asyncpg
import orjson
import pytest
from aiokafka import AIOKafkaConsumer
from asynctest import Mock

from pingeon import KafkaConsumer, Log, Postgres, Status, consumer

pytestmark = pytest.mark.asyncio


async def test_consumer(monkeypatch):
    log = Log(
        uid="48d1a776bb9c4aec9b94c8ab3f446e04",
        status=Status.OK,
        label="wow!",
        start_time=0.1,
        end_time=0.2,
        result={"foo": 0},
    )

    async def aiter(_):
        yield orjson.dumps(log)

    kafka = KafkaConsumer(topic="foo")
    mock_kafka = Mock(spec=AIOKafkaConsumer)
    mock_kafka.__aiter__ = aiter
    monkeypatch.setattr(kafka, "client", mock_kafka)
    mock_postgres = Mock(spec=asyncpg.Connection)

    async def get_connection(_):
        return mock_postgres

    monkeypatch.setattr(Postgres, "get_connection", get_connection)
    await consumer(kafka, Postgres())

    mock_postgres.execute.assert_called_once_with(
        "INSERT INTO logs "
        "(uid, label, status, start_time, end_time, result) "
        "VALUES ($1, $2, $3, to_timestamp($4), to_timestamp($5), $6) "
        "ON CONFLICT ON CONSTRAINT uid_key DO NOTHING;",
        "48d1a776bb9c4aec9b94c8ab3f446e04",
        "wow!",
        "ok",
        0.1,
        0.2,
        {"foo": 0},
        None,
    )
