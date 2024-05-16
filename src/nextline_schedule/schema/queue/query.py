import strawberry
from strawberry.types import Info

from nextline_schedule.queue import Queue

from .types import ScheduleQueueItem


async def resolve_items(info: Info) -> list[ScheduleQueueItem]:
    queue = info.context['schedule']['queue']
    assert isinstance(queue, Queue)
    ret = [ScheduleQueueItem.from_(item) for item in queue.items]
    return ret


@strawberry.type
class QueryScheduleQueue:
    items: list[ScheduleQueueItem] = strawberry.field(resolver=resolve_items)
