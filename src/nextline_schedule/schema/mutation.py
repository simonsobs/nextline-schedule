import strawberry
from strawberry.types import Info


async def mutate_turn_on(info: Info) -> bool:
    auto_mode = info.context["auto_mode"]
    await auto_mode.turn_on()
    return True


async def mutate_turn_off(info: Info) -> bool:
    auto_mode = info.context["auto_mode"]
    await auto_mode.turn_off()
    return True


@strawberry.type
class MutationAutoMode:
    turn_on: bool = strawberry.field(resolver=mutate_turn_on)
    turn_off: bool = strawberry.field(resolver=mutate_turn_off)


@strawberry.type
class MutationSchedule:
    @strawberry.field
    def auto_mode(self, info: Info) -> MutationAutoMode:
        return MutationAutoMode()


@strawberry.type
class Mutation:
    @strawberry.field
    def schedule(self, info: Info) -> MutationSchedule:
        return MutationSchedule()
