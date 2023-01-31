import strawberry
from strawberry.types import Info


def query_auto_mode_state(info: Info) -> str:
    auto_mode = info.context["auto_mode"]
    return auto_mode.state


@strawberry.type
class AutoMode:
    state: str = strawberry.field(resolver=query_auto_mode_state)


@strawberry.type
class Schedule:
    @strawberry.field
    def auto_mode(self, info: Info) -> AutoMode:
        print(info.context)
        return AutoMode()


@strawberry.type
class Query:
    @strawberry.field
    def schedule(self, info: Info) -> Schedule:
        return Schedule()
