import strawberry
from hypothesis import given

from nextline_schedule.graphql import QUERY_SCHEDULE_QUEUE_ITEMS
from nextline_schedule.queue import PubSubQueue
from nextline_schedule.queue.strategies import st_pubsub_queue
from nextline_schedule.schema import Query


@given(queue=st_pubsub_queue())
async def test_query(queue: PubSubQueue):
    async with queue:
        context_schedule = {'queue': queue}
        context = {'schedule': context_schedule}
        schema = strawberry.Schema(query=Query)
        resp = await schema.execute(QUERY_SCHEDULE_QUEUE_ITEMS, context_value=context)
        assert resp.data
        assert len(resp.data['schedule']['queue']['items']) == len(queue.items)
