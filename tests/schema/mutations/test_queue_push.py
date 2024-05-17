from typing import Any, TypedDict

from deepdiff import DeepDiff
from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_schedule.graphql import MUTATE_QUEUE_PUSH
from nextline_schedule.queue.strategies import Queue, st_push_arg, st_queue
from tests.schema.conftest import Schema


class Input(TypedDict):
    name: str
    script: str


@st.composite
def st_input(draw: st.DrawFn) -> Input:
    push_arg = draw(st_push_arg())
    return {'name': push_arg.name, 'script': push_arg.script}


@settings(phases=(Phase.generate,))  # To avoid shrinking
@given(queue=st_queue(), input=st_input())
async def test_schema(queue: Queue, input: Input, schema: Schema) -> None:
    '''

    NOTE: Only the generate phase is included in the settings. This is because
    the shrink phase doesn't make much difference and only takes much longer
    time to run. (https://hypothesis.readthedocs.io/en/latest/settings.html)
    '''
    async with queue:
        len_ini = len(queue.items)

        context_values = {'schedule': {'queue': queue}}
        variable_values = {'input': input}

        resp = await schema.execute(
            MUTATE_QUEUE_PUSH,
            context_value=context_values,
            variable_values=variable_values,
        )
        assert (data := resp.data)
        assert_data(data, input)
        assert_queue_item(queue, data, input, len_ini)


def assert_data(data: dict[str, Any], input: Input) -> None:
    ref_resp_data = {
        'schedule': {
            'queue': {
                'push': {
                    'name': input['name'],
                    'script': input['script'],
                }
            }
        }
    }

    # The 'id' and 'createdAt' are excluded from the reference response data
    # because their values are generated and not part of the input data.
    expected_diff = {
        'dictionary_item_removed': [
            "root['schedule']['queue']['push']['id']",
            "root['schedule']['queue']['push']['createdAt']",
        ]
    }

    diff = DeepDiff(data, ref_resp_data)
    assert diff == expected_diff


def assert_queue_item(
    queue: Queue, data: dict[str, Any], input: Input, len_ini: int
) -> None:
    assert len(queue.items) == len_ini + 1

    id = data['schedule']['queue']['push']['id']
    created_at = data['schedule']['queue']['push']['createdAt']

    last_item = queue.items[-1]

    assert last_item.id == id
    assert last_item.name == input['name']
    assert last_item.script == input['script']
    assert last_item.created_at.isoformat() == created_at
