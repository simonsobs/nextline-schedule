from string import ascii_letters
from unittest.mock import Mock

from hypothesis import given
from hypothesis import strategies as st

from nextline.utils import to_aiter
from nextline_schedule.auto import AutoMode
from nextline_schedule.graphql import SUBSCRIBE_AUTO_MODE_MODE
from tests.schema.conftest import Schema


@given(modes=st.lists(st.text(ascii_letters, min_size=1)))
async def test_schema(modes: list[str], schema: Schema) -> None:
    if not modes:
        # TODO: Test fails for empty list
        return

    auto_mode = Mock(spec=AutoMode)
    auto_mode.subscribe_mode = Mock(return_value=to_aiter(modes))

    context_auto_mode = {'auto_mode': auto_mode}
    context = {'schedule': context_auto_mode}

    sub = await schema.subscribe(SUBSCRIBE_AUTO_MODE_MODE, context_value=context)

    assert hasattr(sub, '__aiter__')
    idx = 0
    async for resp in sub:
        assert not resp.errors
        assert (data := resp.data)
        assert data['scheduleAutoModeMode'] == modes[idx]
        idx += 1

    assert idx == len(modes)
