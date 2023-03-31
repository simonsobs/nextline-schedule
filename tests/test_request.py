import httpx
import pytest
from pytest_httpx import HTTPXMock

from nextline_schedule.scheduler import RequestStatement

COMMANDS = '''
import time
# 2023-03-31 16:12:59
time.sleep(7.61)
time.sleep(5.45)
time.sleep(11.82)
time.sleep(35.12)
'''.lstrip()


async def test_success(httpx_mock: HTTPXMock) -> None:
    json = {
        'commands': COMMANDS,
        # 'message': 'Success',
        # 'status': 'ok',
    }
    httpx_mock.add_response(json=json)
    func = RequestStatement(
        api_url='https://scheduler-uobd.onrender.com/api/v1/schedule/',
        length_minutes=1,
        policy='dummy',
    )

    statement = await func()
    assert statement == COMMANDS


async def test_400(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=400)
    func = RequestStatement(
        api_url='https://scheduler-uobd.onrender.com/api/v1/schedule/',
        length_minutes=1,
        policy='dummy',
    )

    with pytest.raises(RuntimeError):
        await func()


async def test_timeout(httpx_mock: HTTPXMock) -> None:

    httpx_mock.add_exception(httpx.ReadTimeout('timeout'))

    func = RequestStatement(
        api_url='https://scheduler-uobd.onrender.com/api/v1/schedule/',
        length_minutes=1,
        policy='dummy',
    )

    with pytest.raises(httpx.TimeoutException):
        await func()


@pytest.mark.skip
async def test_with_dummy_server() -> None:
    func = RequestStatement(
        api_url='https://scheduler-uobd.onrender.com/api/v1/schedule/',
        length_minutes=1,
        policy='dummy',
    )

    statement = await func()
    print(statement)
