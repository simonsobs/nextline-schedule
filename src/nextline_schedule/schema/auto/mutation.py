import strawberry
from strawberry.types import Info

from nextline_schedule.auto import AutoMode


async def mutate_turn_on(info: Info) -> bool:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoMode)
    await auto_mode.turn_on()
    return True


async def mutate_turn_off(info: Info) -> bool:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoMode)
    await auto_mode.turn_off()
    return True


@strawberry.type
class MutationScheduleAutoMode:
    turn_on: bool = strawberry.field(resolver=mutate_turn_on)
    turn_off: bool = strawberry.field(resolver=mutate_turn_off)
