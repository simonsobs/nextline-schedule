import strawberry
from strawberry.types import Info

from nextline_schedule.auto import AutoMode


def query_auto_mode_state(info: Info) -> str:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoMode)
    return auto_mode.state


@strawberry.type
class QueryScheduleAutoMode:
    state: str = strawberry.field(resolver=query_auto_mode_state)
