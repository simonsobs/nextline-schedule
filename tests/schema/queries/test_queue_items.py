from hypothesis import given
from strawberry.types import ExecutionResult

from nextline_schedule.graphql import QUERY_QUEUE_ITEMS
from nextline_schedule.queue.strategies import Queue, st_queue
from tests.schema.conftest import Schema


@given(queue=st_queue())
async def test_schema(queue: Queue, schema: Schema) -> None:
    async with queue:
        context_schedule = {'queue': queue}
        context = {'schedule': context_schedule}
        resp = await schema.execute(QUERY_QUEUE_ITEMS, context_value=context)
        assert isinstance(resp, ExecutionResult)
        assert resp.data
        assert len(resp.data['schedule']['queue']['items']) == len(queue.items)
