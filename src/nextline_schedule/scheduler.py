import datetime
from logging import getLogger

import httpx


class Scheduler:
    def __init__(self, api_url: str, length_minutes: int, policy: str, timeout=5.0):
        self._api_url = api_url
        self._length_minutes = length_minutes
        self._policy = policy
        self._timeout = timeout
        self._logger = getLogger(__name__)

    async def __call__(self) -> str:
        # https://github.com/simonsobs/scheduler-server?tab=readme-ov-file#request
        start_time = datetime.datetime.utcnow()
        duration = datetime.timedelta(minutes=self._length_minutes)
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
