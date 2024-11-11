from unittest.mock import Mock

from nextline_schedule.auto import AutoMode
from nextline_schedule.graphql import QUERY_AUTO_MODE_MODE
from tests.schema.conftest import Schema


async def test_schema(schema: Schema) -> None:
    auto_mode = Mock(spec=AutoMode)
    mode = 'off'
    auto_mode.mode = mode
    context_auto_mode = {'auto_mode': auto_mode}
    context = {'schedule': context_auto_mode}
    resp = await schema.execute(QUERY_AUTO_MODE_MODE, context_value=context)
    assert (data := resp.data)
    expected = {'schedule': {'autoMode': {'mode': mode}}}
    assert data == expected
