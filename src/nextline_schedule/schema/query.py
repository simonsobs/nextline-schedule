import strawberry

from nextline_schedule import __version__

from .auto import QueryScheduleAutoMode
from .queue import QueryScheduleQueue
from .scheduler import QueryScheduleScheduler


@strawberry.type
class QuerySchedule:
    version: str = __version__

    @strawberry.field
    def auto_mode(self) -> QueryScheduleAutoMode:
        return QueryScheduleAutoMode()

    @strawberry.field
    def scheduler(self) -> QueryScheduleScheduler:
        return QueryScheduleScheduler()

    @strawberry.field
    def queue(self) -> QueryScheduleQueue:
        return QueryScheduleQueue()


@strawberry.type
class Query:
    @strawberry.field
    def schedule(self) -> QuerySchedule:
        return QuerySchedule()
