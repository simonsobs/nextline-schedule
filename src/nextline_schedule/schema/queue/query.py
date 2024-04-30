import datetime

import strawberry
from strawberry.types import Info

from nextline_schedule.queue import Queue, QueueItem


@strawberry.type
class QueryScheduleQueueItem:
    name: str
    created_at: datetime.datetime
    script: str

    @classmethod
    def from_(cls, src: QueueItem) -> 'QueryScheduleQueueItem':
        return cls(
            name=src.name,
            created_at=src.created_at,
            script=src.script,
        )


async def resolve_items(info: Info) -> list[QueryScheduleQueueItem]:
    queue = info.context['schedule']['queue']
    assert isinstance(queue, Queue)
    ret = [QueryScheduleQueueItem.from_(item) for item in queue.items]
    return ret


@strawberry.type
class QueryScheduleQueue:
    items: list[QueryScheduleQueueItem] = strawberry.field(resolver=resolve_items)
