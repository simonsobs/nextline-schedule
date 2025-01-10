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
class ScheduleSchedulerPreviewItem:
    script: str
    # TODO: Add metadata, e.g., timestamp, etc.


async def query_scheduler_preview(info: Info) -> ScheduleSchedulerPreviewItem:
    scheduler = info.context['schedule']['scheduler']
    assert callable(scheduler)
    statement = await scheduler()
    assert isinstance(statement, str)
    return ScheduleSchedulerPreviewItem(script=statement)


@strawberry.type
class QueryScheduleScheduler:
    api_url: str = strawberry.field(resolver=query_scheduler_api_url)
    length_minutes: int = strawberry.field(resolver=query_scheduler_length_minutes)
    policy: str = strawberry.field(resolver=query_scheduler_policy)
    preview: ScheduleSchedulerPreviewItem = strawberry.field(
        resolver=query_scheduler_preview
    )
