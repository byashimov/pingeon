from .repositories import KafkaConsumer, Postgres


async def consumer(kafka: KafkaConsumer, postgres: Postgres):
    async with postgres, kafka:
        async for result in kafka.read():
            await postgres.save(result)
