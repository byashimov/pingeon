from dataclasses import dataclass, field
from typing import AsyncIterator, Union

import asyncpg
import orjson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .models import Log


class BaseKafka:
    # This is not abstract class, because I prefer to us mypy
    client: Union[AIOKafkaProducer, AIOKafkaConsumer]

    async def __aenter__(self) -> None:
        await self.client.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.client.stop()


@dataclass
class KafkaProducer(BaseKafka):
    topic: str
    client: AIOKafkaProducer

    async def send(self, obj: Log) -> None:
        # todo: add reconnects, statsd
        data: bytes = orjson.dumps(obj)
        await self.client.send_and_wait(self.topic, data)


@dataclass
class KafkaConsumer(BaseKafka):
    topic: str
    client: AIOKafkaConsumer

    async def read(self) -> AsyncIterator[Log]:
        # todo: add reconnects, statsd
        async for msg in self.client:
            yield Log(**orjson.loads(msg))


@dataclass
class Postgres:
    user: str = "user"
    password: str = "password"
    database: str = "database"
    host: str = "127.0.0.1"
    conn: asyncpg.Connection = field(init=False)

    async def get_connection(self) -> asyncpg.Connection:
        return await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
        )

    async def __aenter__(self) -> None:
        self.conn = await self.get_connection()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.conn.close()

    async def save(self, obj: Log):
        """
        Saves log idempotent
        """

        # fixme: prepared statement doesn't work with pgbouncer
        await self.conn.execute(
            "INSERT INTO logs "
            "(uid, label, status, start_time, end_time, result) "
            "VALUES ($1, $2, $3, to_timestamp($4), to_timestamp($5), $6) "
            "ON CONFLICT ON CONSTRAINT log_key "
            "DO NOTHING;",
            obj.uid,
            obj.label,
            obj.status,
            obj.start_time,
            obj.end_time,
            obj.result,
        )
