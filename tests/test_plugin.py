import asyncio
from collections.abc import AsyncIterator

import pytest
from pytest_httpx import HTTPXMock

from nextline_schedule.graphql import (
    MUTATE_AUTO_MODE_TURN_OFF,
    MUTATE_AUTO_MODE_TURN_ON,
    QUERY_AUTO_MODE_STATE,
    QUERY_SCHEDULER,
    SUBSCRIBE_AUTO_MODE_STATE,
)
from nextlinegraphql import create_app
from nextlinegraphql.plugins.ctrl.graphql import SUBSCRIBE_STATE
from nextlinegraphql.plugins.graphql.test import TestClient, gql_request, gql_subscribe


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    app = create_app()  # the plugin is loaded here
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y


# TODO: Update the test so that `can_send_already_matched_responses` is not needed
#       This option is used to pass the test with `pytest-httpx>=0.32.0``
#       https://github.com/Colin-b/pytest_httpx/releases/tag/v0.32.0
#       https://github.com/Colin-b/pytest_httpx/blob/v0.32.0/README.md#allow-to-register-a-response-for-more-than-one-request


@pytest.mark.httpx_mock(can_send_already_matched_responses=True)
async def test_plugin(client: TestClient) -> None:
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

    data = await gql_request(client, QUERY_AUTO_MODE_STATE)
    expected = {'schedule': {'autoMode': {'state': 'off'}}}
    assert data == expected

    data = await gql_request(client, MUTATE_AUTO_MODE_TURN_ON)

    n_runs = 0
    async for data in gql_subscribe(client, SUBSCRIBE_STATE):  # pragma: no branch
        if data['ctrlState'] == 'running':
            turned_on.set()
            n_runs += 1
        if n_runs >= 3:
            data = await gql_request(client, MUTATE_AUTO_MODE_TURN_OFF)
            break

    async for data in gql_subscribe(client, SUBSCRIBE_STATE):  # pragma: no branch
        if data['ctrlState'] == 'finished':
            break

    await task


async def subscribe_auto_mode_state(
    client: TestClient, turned_on: asyncio.Event
) -> list[str]:
    await turned_on.wait()
    ret = []
    async for data in gql_subscribe(
        client, SUBSCRIBE_AUTO_MODE_STATE
    ):  # pragma: no branch
        state = data['scheduleAutoModeState']
        ret.append(state)
        if state == 'off':
            break
    return ret


@pytest.fixture(autouse=True)
def configure_by_envvar(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('NEXTLINE_SCHEDULE__API', 'https://example.com')
    monkeypatch.setenv('NEXTLINE_SCHEDULE__LENGTH_MINUTES', '60')
    monkeypatch.setenv('NEXTLINE_SCHEDULE__POLICY', 'test')


COMMANDS = '''
import time
time.sleep(0.001)
'''.lstrip()


@pytest.fixture(autouse=True)
def mock_httpx(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={'commands': COMMANDS})
