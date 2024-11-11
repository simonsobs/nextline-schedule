from string import ascii_letters
from unittest.mock import Mock

from hypothesis import given, provisional
from hypothesis import strategies as st

from nextline_schedule.graphql import QUERY_SCHEDULER
from nextline_schedule.scheduler import Scheduler
from nextline_test_utils.strategies import st_graphql_ints
from tests.schema.conftest import Schema


@given(d=st.data())
async def test_schema(d: st.DataObject, schema: Schema) -> None:
    api_url = d.draw(provisional.urls())
    length_minutes = d.draw(st_graphql_ints(min_value=1))
    policy = d.draw(st.text(ascii_letters, min_size=1))

    scheduler = Mock(spec=Scheduler)
    scheduler._api_url = api_url
    scheduler._length_minutes = length_minutes
    scheduler._policy = policy

    context = {'schedule': {'scheduler': scheduler}}
    resp = await schema.execute(QUERY_SCHEDULER, context_value=context)
    assert (data := resp.data)

    expected = {
        'schedule': {
            'scheduler': {
                'apiUrl': api_url,
                'lengthMinutes': length_minutes,
                'policy': policy,
            }
        }
    }
    assert data == expected
