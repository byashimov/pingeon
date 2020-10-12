from functools import partial

import orjson
import pytest
from aiokafka import AIOKafkaProducer
from asynctest import Mock
from hamcrest import assert_that, has_entries, instance_of

from pingeon import KafkaProducer, producer, site_check

pytestmark = pytest.mark.asyncio


async def test_producer_with_site_check(httpx_mock):
    httpx_mock.add_response(status_code=200, data="wassup!")
    mock_client = Mock(spec=AIOKafkaProducer)
    kafka = KafkaProducer(topic="topic", client=mock_client)
    checkers = {"site_check": partial(site_check, "http://foo", "sup")}
    await producer(kafka, checkers)

    # Client asserts
    mock_client.start.assert_called_once()
    mock_client.stop.assert_called_once()
    mock_client.send_and_wait.assert_called_once()

    # Data asserts
    topic, data = mock_client.send_and_wait.call_args[0]
    assert topic == "topic"
    assert isinstance(data, bytes)

    # Log asserts
    expected = has_entries(
        uid=instance_of(str),
        label="site_check",
        status="ok",
        start_time=instance_of(float),
        end_time=instance_of(float),
        result=instance_of(dict),
    )
    assert_that(orjson.loads(data), expected)
