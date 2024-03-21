import strawberry

import nextline_schedule
from nextline_schedule.graphql import QUERY_VERSION
from nextline_schedule.schema import Query


async def test_version():
    schema = strawberry.Schema(query=Query)
    resp = await schema.execute(QUERY_VERSION)
    assert resp.data['schedule']['version'] == nextline_schedule.__version__
