from typing import TypedDict
from unittest.mock import Mock

from deepdiff import DeepDiff
from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_schedule.graphql import MUTATE_QUEUE_PUSH
from nextline_schedule.queue import PushArg, Queue, QueueItem
from nextline_schedule.queue.strategies import st_push_arg
from nextline_test_utils.strategies import st_datetimes, st_graphql_ints
from tests.schema.conftest import Schema


class Input(TypedDict):
    name: str
    script: str


@st.composite
def st_input(draw: st.DrawFn) -> Input:
    push_arg = draw(st_push_arg())
    return {'name': push_arg.name, 'script': push_arg.script}


@settings(phases=(Phase.generate,))  # To avoid shrinking
@given(d=st.data())
async def test_schema(d: st.DataObject, schema: Schema) -> None:
    input = d.draw(st_input())
    item = QueueItem(
        **input,
        id=d.draw(st_graphql_ints(min_value=1)),
        created_at=d.draw(st_datetimes()),
    )

    queue = Mock(spec=Queue)
    queue.push.return_value = item

    context_values = {'schedule': {'queue': queue}}
    variable_values = {'input': input}

    resp = await schema.execute(
        MUTATE_QUEUE_PUSH,
        context_value=context_values,
        variable_values=variable_values,
    )

    assert (data := resp.data)
    expected_data = {
        'schedule': {
            'queue': {
                'push': {
                    'name': item.name,
                    'script': item.script,
                    'id': item.id,
                    'createdAt': item.created_at.isoformat(),
                }
            }
        }
    }
    assert DeepDiff(data, expected_data) == {}

    queue.push.assert_awaited_once_with(PushArg(**input))
