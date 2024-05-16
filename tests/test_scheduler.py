import datetime
import json
import unittest.mock as mock

import httpx
import pytest
from pytest_httpx import HTTPXMock

from nextline_schedule.scheduler import Scheduler
from nextline_schedule.utils.utc import is_timezone_aware

MOCK_URL = 'https://scheduler-uobd.onrender.com/api/v1/schedule/'

MOCK_UTCNOW = datetime.datetime(2023, 3, 31, 16, 12, 59)
assert not is_timezone_aware(MOCK_UTCNOW)

COMMANDS = '''
import time
# 2023-03-31 16:12:59
time.sleep(7.61)
time.sleep(5.45)
time.sleep(11.82)
time.sleep(35.12)
'''.lstrip()


async def test_success(httpx_mock: HTTPXMock) -> None:
    data = {
        'commands': COMMANDS,
        # 'message': 'Success',
        # 'status': 'ok',
    }
    httpx_mock.add_response(json=data)
    func = Scheduler(api_url=MOCK_URL, length_minutes=1, policy='dummy')

    statement = await func()
    assert statement == COMMANDS

    assert (request := httpx_mock.get_request())

    assert request.method == 'POST'
    assert request.url == MOCK_URL

    expected_content = {
        't0': '2023-03-31 16:12',
        't1': '2023-03-31 16:13',
        'policy': 'dummy',
    }
    assert json.loads(request.content) == expected_content


async def test_400(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=400)
    func = Scheduler(api_url=MOCK_URL, length_minutes=1, policy='dummy')

    with pytest.raises(RuntimeError):
        await func()


async def test_timeout(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.ReadTimeout('timeout'))
    func = Scheduler(api_url=MOCK_URL, length_minutes=1, policy='dummy')

    with pytest.raises(httpx.TimeoutException):
        await func()


@pytest.mark.skip
async def test_with_dummy_server() -> None:
    # https://simonsobs.slack.com/archives/D03TBRKRRQ9/p1689280148455099
    test_api_url = 'https://scheduler-uobd.onrender.com/api/v1/schedule/'
    func = Scheduler(api_url=test_api_url, length_minutes=1, policy='dummy')

    statement = await func()
    print(statement)


@pytest.fixture(autouse=True)
def mock_datetime_utcnow(monkeypatch: pytest.MonkeyPatch) -> mock.Mock:
    from nextline_schedule import scheduler

    m = mock.Mock(wraps=datetime)
    m.datetime.utcnow.return_value = MOCK_UTCNOW
    monkeypatch.setattr(scheduler, 'datetime', m)

    return m
