from collections.abc import AsyncIterator

from strawberry.types import Info

from nextline_schedule.queue import PubSubQueue

from .types import QueryScheduleQueueItem


async def subscribe_schedule_queue_items(
    info: Info,
) -> AsyncIterator[list[QueryScheduleQueueItem]]:
    queue = info.context['schedule']['queue']
    assert isinstance(queue, PubSubQueue)
    async for items in queue.subscribe():
        yield [QueryScheduleQueueItem.from_(item) for item in items]
