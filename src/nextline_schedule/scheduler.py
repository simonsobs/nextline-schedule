import random
from datetime import datetime, timedelta

import httpx

# https://github.com/simonsobs/so-scheduler/blob/master/readme.md#schedule-api
API_URL = 'https://scheduler-uobd.onrender.com/api/v1/schedule/'


class RequestStatement:
    def __init__(self):
        self._api_url = API_URL
        self._length_minutes = 1
        self._policy = 'dummy'

    async def __call__(self) -> str:
        start_time = datetime.utcnow()
        duration = timedelta(minutes=self._length_minutes)
        end_time = start_time + duration
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M')
        data = {"t0": start_time_str, "t1": end_time_str, "policy": self._policy}
        print(data)
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json=data)
        print(response.json())
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
