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


async def mutate_change_mode(info: Info, mode: str) -> bool:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoMode)
    if mode not in ('off', 'scheduler', 'queue'):
        return False
    await auto_mode.change_mode(mode)  # type: ignore
    return True


@strawberry.type
class MutationScheduleAutoMode:
    turn_on: bool = strawberry.mutation(resolver=mutate_turn_on)
    turn_off: bool = strawberry.mutation(resolver=mutate_turn_off)
    change_mode: bool = strawberry.mutation(resolver=mutate_change_mode)
