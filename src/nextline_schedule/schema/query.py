from typing import cast

import strawberry
from strawberry.types import Info

from nextline_schedule import __version__
from nextline_schedule.schedule import Schedule


def query_auto_mode_state(info: Info) -> str:
    schedule = cast(Schedule, info.context['schedule'])
    auto_mode = schedule.auto_mode
    return auto_mode.state


@strawberry.type
class QueryAutoMode:
    state: str = strawberry.field(resolver=query_auto_mode_state)


def query_scheduler_api_url(info: Info) -> str:
    schedule = cast(Schedule, info.context['schedule'])
    scheduler = schedule.scheduler
    return scheduler._api_url


def query_scheduler_length_minutes(info: Info) -> int:
    schedule = cast(Schedule, info.context['schedule'])
    scheduler = schedule.scheduler
    return scheduler._length_minutes


def query_scheduler_policy(info: Info) -> str:
    schedule = cast(Schedule, info.context['schedule'])
    scheduler = schedule.scheduler
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
    def auto_mode(self, info: Info) -> QueryAutoMode:
        return QueryAutoMode()

    @strawberry.field
    def scheduler(self, info: Info) -> QueryScheduler:
        return QueryScheduler()


@strawberry.type
class Query:
    @strawberry.field
    def schedule(self, info: Info) -> QuerySchedule:
        return QuerySchedule()
