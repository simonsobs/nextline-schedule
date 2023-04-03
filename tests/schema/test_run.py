import asyncio

import pytest
from async_asgi_testclient import TestClient
from nextlinegraphql.plugins.ctrl.graphql import SUBSCRIBE_STATE
from nextlinegraphql.plugins.graphql.test import gql_request, gql_subscribe
from pytest_httpx import HTTPXMock

from nextline_schedule.graphql import (
    MUTATE_AUTO_MODE_TURN_OFF,
    MUTATE_AUTO_MODE_TURN_ON,
    QUERY_AUTO_MODE,
    QUERY_SCHEDULER,
    SUBSCRIBE_AUTO_MODE_STATE,
)


async def test_run(client: TestClient):

    turned_on = asyncio.Event()
    task = asyncio.create_task(subscribe_auto_mode_state(client, turned_on))

    data = await gql_request(client, QUERY_SCHEDULER)
    expected = {
        'schedule': {
            'scheduler': {
                'apiUrl': 'https://example.com',
                'lengthMinutes': 60,
                'policy': 'test',
            }
        }
    }
    assert data == expected

    data = await gql_request(client, QUERY_AUTO_MODE)
    expected = {'schedule': {'autoMode': {'state': 'off'}}}
    assert data == expected

    data = await gql_request(client, MUTATE_AUTO_MODE_TURN_ON)

    n_runs = 0
    async for data in gql_subscribe(client, SUBSCRIBE_STATE):
        if data['state'] == 'running':
            turned_on.set()
            n_runs += 1
        if n_runs >= 3:
            data = await gql_request(client, MUTATE_AUTO_MODE_TURN_OFF)
            break

    async for data in gql_subscribe(client, SUBSCRIBE_STATE):
        if data['state'] == 'finished':
            break

    await task


async def subscribe_auto_mode_state(client: TestClient, turned_on: asyncio.Event):
    await turned_on.wait()
    ret = []
    async for data in gql_subscribe(client, SUBSCRIBE_AUTO_MODE_STATE):
        state = data['scheduleAutoModeState']
        ret.append(state)
        if state == 'off':
            break
    return ret


@pytest.fixture(autouse=True)
def configure_by_envvar(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('NEXTLINE_SCHEDULE__API', 'https://example.com')
    monkeypatch.setenv('NEXTLINE_SCHEDULE__LENGTH_MINUTES', '60')
    monkeypatch.setenv('NEXTLINE_SCHEDULE__POLICY', 'test')


COMMANDS = '''
import time
time.sleep(0.001)
'''.lstrip()


@pytest.fixture(autouse=True)
def mock_httpx(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={'commands': COMMANDS})
