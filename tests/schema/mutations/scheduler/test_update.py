from string import ascii_letters
from typing import TypedDict
from unittest.mock import Mock

from deepdiff import DeepDiff
from hypothesis import Phase, given, provisional, settings
from hypothesis import strategies as st

from nextline_schedule.graphql import MUTATE_SCHEDULER_UPDATE
from nextline_schedule.scheduler import Scheduler
from nextline_test_utils.strategies import st_graphql_ints, st_none_or
from tests.schema.conftest import Schema


class Input(TypedDict):
    apiUrl: str | None
    lengthMinutes: int | None
    policy: str | None


@st.composite
def st_input(draw: st.DrawFn) -> Input:
    apiUrl = draw(st_none_or(provisional.urls()))
    lengthMinutes = draw(st_none_or(st_graphql_ints(min_value=1)))
    policy = draw(st_none_or(st.text(ascii_letters, min_size=1)))
    return {'apiUrl': apiUrl, 'lengthMinutes': lengthMinutes, 'policy': policy}


@settings(phases=(Phase.generate,))  # To avoid shrinking
@given(d=st.data())
async def test_schema(d: st.DataObject, schema: Schema) -> None:
    input = d.draw(st_input())

    init_api_url = d.draw(provisional.urls())
    init_length_minutes = d.draw(st_graphql_ints(min_value=1))
    init_policy = d.draw(st.text(ascii_letters, min_size=1))

    scheduler = Mock(spec=Scheduler)
    scheduler._api_url = init_api_url
    scheduler._length_minutes = init_length_minutes
    scheduler._policy = init_policy

    context_values = {'schedule': {'scheduler': scheduler}}
    variable_values = {'input': input}

    resp = await schema.execute(
        MUTATE_SCHEDULER_UPDATE,
        context_value=context_values,
        variable_values=variable_values,
    )

    assert (data := resp.data)
    expected_data = {'schedule': {'scheduler': {'update': True}}}
    assert DeepDiff(data, expected_data) == {}

    if input['apiUrl'] is not None:
        assert scheduler._api_url == input['apiUrl']
    else:
        assert scheduler._api_url == init_api_url

    if input['lengthMinutes'] is not None:
        assert scheduler._length_minutes == input['lengthMinutes']
    else:
        assert scheduler._length_minutes == init_length_minutes

    if input['policy'] is not None:
        assert scheduler._policy == input['policy']
    else:
        assert scheduler._policy == init_policy
