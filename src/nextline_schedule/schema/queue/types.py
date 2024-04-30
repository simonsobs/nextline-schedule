import datetime

import strawberry

from nextline_schedule.queue import QueueItem


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
