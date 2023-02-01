import strawberry
from strawberry.types import Info


def query_auto_mode_state(info: Info) -> str:
    auto_mode = info.context["auto_mode"]
    return auto_mode.state


@strawberry.type
class QueryAutoMode:
    state: str = strawberry.field(resolver=query_auto_mode_state)


def query_scheduler_api_url(info: Info) -> str:
    scheduler = info.context["scheduler"]
    return scheduler._api_url


def query_scheduler_length_minutes(info: Info) -> int:
    scheduler = info.context["scheduler"]
    return scheduler._length_minutes


def query_scheduler_policy(info: Info) -> str:
    scheduler = info.context["scheduler"]
    return scheduler._policy


@strawberry.type
class QueryScheduler:
    api_url: str = strawberry.field(resolver=query_scheduler_api_url)
    length_minutes: int = strawberry.field(resolver=query_scheduler_length_minutes)
    policy: str = strawberry.field(resolver=query_scheduler_policy)


@strawberry.type
class QuerySchedule:
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
