import asyncio

from nextline_graphql.factory import create_app_for_test
from nextline_graphql.plugins.graphql.test import TestClient, gql_request
from nextline_schedule import Plugin
from nextline_schedule.graphql import QUERY_AUTO_MODE_STATE


async def test_app() -> None:
    plugin = Plugin()
    app = create_app_for_test(extra_plugins=[plugin])
    async with TestClient(app) as client:
        # plugin.lifespan() must have been entered.
        await asyncio.sleep(0)

        data = await gql_request(client, QUERY_AUTO_MODE_STATE)
        # plugin.update_strawberry_context() must have been called.

        expected = {'schedule': {'autoMode': {'state': 'off'}}}
        assert data == expected
