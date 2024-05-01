import strawberry
from strawberry.types import Info

from nextline_schedule.queue import PubSubQueue

from .types import QueryScheduleQueueItem


async def resolve_items(info: Info) -> list[QueryScheduleQueueItem]:
    queue = info.context['schedule']['queue']
    assert isinstance(queue, PubSubQueue)
    ret = [QueryScheduleQueueItem.from_(item) for item in queue.items]
    return ret


@strawberry.type
class QueryScheduleQueue:
    items: list[QueryScheduleQueueItem] = strawberry.field(resolver=resolve_items)
