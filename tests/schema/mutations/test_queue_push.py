from hypothesis import given
from hypothesis import strategies as st

from nextline_schedule.graphql import MUTATE_QUEUE_PUSH
from nextline_schedule.queue.strategies import Queue, st_push_arg, st_queue
from tests.schema.conftest import Schema


@st.composite
def st_input(draw: st.DrawFn) -> dict:
    push_arg = draw(st_push_arg())
    return {'name': push_arg.name, 'script': push_arg.script}


@given(queue=st_queue(), input=st_input())
async def test_schema(queue: Queue, input: dict, schema: Schema):
    async with queue:
        initial_len = len(queue.items)
        context_schedule = {'queue': queue}
        context = {'schedule': context_schedule}
        variable = {'input': input}
        resp = await schema.execute(
            MUTATE_QUEUE_PUSH, context_value=context, variable_values=variable
        )
        assert resp.data
        ret = resp.data['schedule']['queue']['push']
        assert ret['script'] == input['script']
        assert len(queue.items) == initial_len + 1
