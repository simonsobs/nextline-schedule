import strawberry
from strawberry.types import Info

from nextline_schedule import __version__
from nextline_schedule.scheduler import Scheduler

from .auto import QueryScheduleAutoMode
from .queue import QueryScheduleQueue


def query_scheduler_api_url(info: Info) -> str:
    scheduler = info.context['schedule']['scheduler']
    assert isinstance(scheduler, Scheduler)
    return scheduler._api_url


def query_scheduler_length_minutes(info: Info) -> int:
    scheduler = info.context['schedule']['scheduler']
    assert isinstance(scheduler, Scheduler)
    return scheduler._length_minutes


def query_scheduler_policy(info: Info) -> str:
    scheduler = info.context['schedule']['scheduler']
    assert isinstance(scheduler, Scheduler)
    return scheduler._policy


@strawberry.type
class QueryScheduler:
    api_url: str = strawberry.field(resolver=query_scheduler_api_url)
    length_minutes: int = strawberry.field(resolver=query_scheduler_length_minutes)
    policy: str = strawberry.field(resolver=query_scheduler_policy)


@strawberry.type
class QuerySchedule:
    version: str = __version__

    @strawberry.field
    def auto_mode(self) -> QueryScheduleAutoMode:
        return QueryScheduleAutoMode()

    @strawberry.field
    def scheduler(self) -> QueryScheduler:
        return QueryScheduler()

    @strawberry.field
    def queue(self) -> QueryScheduleQueue:
        return QueryScheduleQueue()


@strawberry.type
class Query:
    @strawberry.field
    def schedule(self) -> QuerySchedule:
        return QuerySchedule()
