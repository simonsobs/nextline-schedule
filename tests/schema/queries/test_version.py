import nextline_schedule
from nextline_schedule.graphql import QUERY_VERSION
from tests.schema.conftest import Schema


async def test_schema(schema: Schema) -> None:
    resp = await schema.execute(QUERY_VERSION)
    assert resp.data
    assert resp.data['schedule']['version'] == nextline_schedule.__version__
