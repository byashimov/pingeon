from typing import Dict, Optional

import httpx

from .utils import timer


class CheckError(Exception):
    pass


async def site_check(url: str, expected_text: Optional[str] = None) -> Dict:
    async with httpx.AsyncClient() as client:
        with timer() as time:
            resp: httpx.Response = await client.get(url)

    if resp.status_code != 200:
        raise CheckError(f'Invalid status code "{resp.status_code}"')

    if expected_text and expected_text not in resp.text:
        raise CheckError(f'Body does not contain "{expected_text}"')

    result = {
        "response_time": time.total,
        "status_code": resp.status_code,
    }
    return result
