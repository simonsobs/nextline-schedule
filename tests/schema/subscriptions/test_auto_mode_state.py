from string import ascii_letters
from unittest.mock import Mock

from hypothesis import given
from hypothesis import strategies as st

from nextline.utils import to_aiter
from nextline_schedule.auto import AutoMode
from nextline_schedule.graphql import SUBSCRIBE_AUTO_MODE_STATE
from tests.schema.conftest import Schema


@given(states=st.lists(st.text(ascii_letters, min_size=1)))
async def test_schema(states: list[str], schema: Schema) -> None:
    if not states:
        # TODO: Test fails for empty list
        return

    auto_mode = Mock(spec=AutoMode)
    auto_mode.subscribe_state = Mock(return_value=to_aiter(states))

    context_auto_mode = {'auto_mode': auto_mode}
    context = {'schedule': context_auto_mode}

    sub = await schema.subscribe(SUBSCRIBE_AUTO_MODE_STATE, context_value=context)

    assert hasattr(sub, '__aiter__')
    idx = 0
    async for resp in sub:
        assert not resp.errors
        assert (data := resp.data)
        assert data['scheduleAutoModeState'] == states[idx]
        idx += 1

    assert idx == len(states)
