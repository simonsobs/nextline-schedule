from typing import Optional

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


@strawberry.input
class MutationSchedulerInput:
    api_url: Optional[str] = None
    length_minutes: Optional[int] = None
    policy: Optional[str] = None


@strawberry.type
class MutationScheduler:
    @strawberry.mutation
    def update(self, info: Info, input: MutationSchedulerInput) -> bool:
        scheduler = info.context["scheduler"]
        if input.api_url is not None:
            scheduler._api_url = input.api_url
        if input.length_minutes is not None:
            scheduler._length_minutes = input.length_minutes
        if input.policy is not None:
            scheduler._policy = input.policy
        return True


@strawberry.type
class MutationSchedule:
    @strawberry.field
    def auto_mode(self, info: Info) -> MutationAutoMode:
        return MutationAutoMode()

    @strawberry.field
    def scheduler(self, info: Info) -> MutationScheduler:
        return MutationScheduler()


@strawberry.type
class Mutation:
    @strawberry.field
    def schedule(self, info: Info) -> MutationSchedule:
        return MutationSchedule()
