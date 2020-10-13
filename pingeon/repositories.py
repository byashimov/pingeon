from dataclasses import dataclass, field
from typing import AsyncIterator, Optional, Union

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
    address: str = "localhost"
    client: AIOKafkaProducer = field(init=False)

    def __post_init__(self):
        self.client = AIOKafkaProducer(
            bootstrap_servers=self.address,
        )

    async def send(self, obj: Log) -> None:
        # todo: add reconnects, statsd
        data: bytes = orjson.dumps(obj)
        await self.client.send_and_wait(self.topic, data)


@dataclass
class KafkaConsumer(BaseKafka):
    topic: str
    address: str = "localhost"
    group_id: Optional[str] = None
    client: AIOKafkaConsumer = field(init=False)

    def __post_init__(self):
        self.client = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.address,
            group_id=self.group_id,
        )

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
    port: Union[str, int] = 5432
    conn: asyncpg.Connection = field(init=False)

    async def get_connection(self) -> asyncpg.Connection:
        return await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=int(self.port),
        )

    async def __aenter__(self) -> None:
        self.conn = await self.get_connection()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.conn.close()

    async def save(self, obj: Log):
        """
        Saves log idempotent, kafka is about at least one delivery
        """

        # fixme: prepared statement doesn't work with pgbouncer
        await self.conn.execute(
            "INSERT INTO logs "
            "(uid, label, status, start_time, end_time, result) "
            "VALUES ($1, $2, $3, to_timestamp($4), to_timestamp($5), $6) "
            "ON CONFLICT ON CONSTRAINT uid_key "
            "DO NOTHING;",
            obj.uid,
            obj.label,
            obj.status,
            obj.start_time,
            obj.end_time,
            obj.result,
        )
