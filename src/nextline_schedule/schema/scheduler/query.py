import strawberry
from strawberry.types import Info

from nextline_schedule.scheduler import Scheduler


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
class QueryScheduleScheduler:
    api_url: str = strawberry.field(resolver=query_scheduler_api_url)
    length_minutes: int = strawberry.field(resolver=query_scheduler_length_minutes)
    policy: str = strawberry.field(resolver=query_scheduler_policy)
