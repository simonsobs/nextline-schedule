import random
from datetime import datetime, timedelta
from logging import getLogger

import httpx


class RequestStatement:
    def __init__(self, api_url: str, length_minutes: int, policy: str, timeout=5.0):
        self._api_url = api_url
        self._length_minutes = length_minutes
        self._policy = policy
        self._timeout = timeout
        self._logger = getLogger(__name__)

    async def __call__(self) -> str:
        # https://github.com/simonsobs/so-scheduler/blob/master/readme.md#schedule-api
        start_time = datetime.utcnow()
        duration = timedelta(minutes=self._length_minutes)
        end_time = start_time + duration
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M')
        data = {"t0": start_time_str, "t1": end_time_str, "policy": self._policy}
        self._logger.info(f'Pulling a script: {data!r}')
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._api_url, json=data, timeout=self._timeout
                )
        except Exception:
            self._logger.exception('')
            raise
        if not response.status_code == 200:
            msg = f'Failed: {response.status_code!r}, {response.text!r}'
            self._logger.error(msg)
            raise RuntimeError(msg)
        self._logger.info(f'Response: {response.json()!r}')
        return response.json()['commands']


class DummyRequestStatement(RequestStatement):
    async def __call__(self) -> str:
        return generate_dummy_statement()


def generate_dummy_statement() -> str:
    s = '\n'.join(
        f'time.sleep({random.uniform(1, 3):.2})' for _ in range(random.randint(5, 10))
    )
    s = '\n'.join(
        (
            f'# {datetime.utcnow().isoformat()}',
            'import time',
            '',
            s,
        )
    )
    return s
