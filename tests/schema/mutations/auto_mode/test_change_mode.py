from string import ascii_lowercase
from unittest.mock import Mock

from deepdiff import DeepDiff
from hypothesis import given
from hypothesis import strategies as st

from nextline_schedule.auto import AutoMode
from nextline_schedule.graphql import MUTATE_AUTO_MODE_CHANGE_MODE
from tests.schema.conftest import Schema

MODES = ['off', 'scheduler', 'queue']


@given(mode=st.one_of(st.sampled_from(MODES), st.text(ascii_lowercase, min_size=1)))
async def test_schema(mode: str, schema: Schema) -> None:
    valid = mode in MODES
    auto_mode = Mock(spec=AutoMode)
    context_auto_mode = {'auto_mode': auto_mode}
    context_value = {'schedule': context_auto_mode}
    variable_values = {'mode': mode}
    resp = await schema.execute(
        MUTATE_AUTO_MODE_CHANGE_MODE,
        context_value=context_value,
        variable_values=variable_values,
    )
    assert (data := resp.data)
    expected = {'schedule': {'autoMode': {'changeMode': valid}}}
    assert DeepDiff(data, expected) == {}
    if valid:
        auto_mode.change_mode.assert_awaited_once_with(mode)
