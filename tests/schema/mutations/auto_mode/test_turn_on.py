from unittest.mock import Mock

from nextline_schedule.auto import AutoMode
from nextline_schedule.graphql import MUTATE_AUTO_MODE_TURN_ON
from tests.schema.conftest import Schema


async def test_schema(schema: Schema) -> None:
    auto_mode = Mock(spec=AutoMode)
    context_auto_mode = {'auto_mode': auto_mode}
    context_value = {'schedule': context_auto_mode}
    resp = await schema.execute(MUTATE_AUTO_MODE_TURN_ON, context_value=context_value)
    assert (data := resp.data)
    expected = {'schedule': {'autoMode': {'turnOn': True}}}
    assert data == expected
    auto_mode.turn_on.assert_awaited_once()
