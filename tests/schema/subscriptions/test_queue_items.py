from unittest.mock import Mock

from deepdiff import DeepDiff
from hypothesis import given, settings
from hypothesis import strategies as st

from nextline.utils import to_aiter
from nextline_schedule.graphql import SUBSCRIBE_QUEUE_ITEMS
from nextline_schedule.queue.strategies import Queue, QueueItem, st_queue_item_list
from tests.schema.conftest import Schema


@settings(deadline=None)
@given(item_lists=st.lists(st_queue_item_list(max_size=5), max_size=10))
async def test_schema(item_lists: list[list[QueueItem]], schema: Schema) -> None:
    if not item_lists:
        # TODO: Test fails for empty list
        return

    queue = Mock(spec=Queue)
    queue.subscribe = Mock(return_value=to_aiter(item_lists))

    context_schedule = {'queue': queue}
    context = {'schedule': context_schedule}

    sub = await schema.subscribe(SUBSCRIBE_QUEUE_ITEMS, context_value=context)

    assert hasattr(sub, '__aiter__')
    idx = 0
    async for resp in sub:
        assert not resp.errors
        assert (data := resp.data)
        expected = [
            {
                'name': item.name,
                'script': item.script,
                'id': item.id,
                'createdAt': item.created_at.isoformat(),
            }
            for item in item_lists[idx]
        ]
        actual = data['scheduleQueueItems']
        assert DeepDiff(actual, expected) == {}

        idx += 1

    assert idx == len(item_lists)
