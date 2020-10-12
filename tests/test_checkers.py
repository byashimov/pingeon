import pytest

from pingeon import CheckError, site_check

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("text, expected_text", (("", None), ("foobarbaz", "foo")))
async def test_site_check_ok(httpx_mock, text, expected_text):
    httpx_mock.add_response(status_code=200, data=text)
    result = await site_check("https://localhost", expected_text=expected_text)
    assert result["status_code"] == 200
    assert isinstance(result["response_time"], float)


@pytest.mark.parametrize(
    "status, text, error",
    (
        (200, "", 'Body does not contain "foo"'),
        (200, "wow!", 'Body does not contain "foo"'),
        (400, "foo", 'Invalid status code "400"'),
        (500, "", 'Invalid status code "500"'),
    ),
)
async def test_site_check_fails(httpx_mock, status, text, error):
    httpx_mock.add_response(status_code=status, data=text)
    with pytest.raises(CheckError, match=error):
        await site_check("https://foo", expected_text="foo")
