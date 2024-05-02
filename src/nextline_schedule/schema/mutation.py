from typing import Optional

import strawberry
from nextline import Nextline
from strawberry.types import Info

from nextline_schedule.auto import AutoMode
from nextline_schedule.scheduler import RequestStatement

from .queue import MutationScheduleQueue


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
        scheduler = info.context['schedule']['scheduler']
        assert isinstance(scheduler, RequestStatement)
        if input.api_url is not None:
            scheduler._api_url = input.api_url
        if input.length_minutes is not None:
            scheduler._length_minutes = input.length_minutes
        if input.policy is not None:
            scheduler._policy = input.policy
        return True


async def mutate_load_script(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    scheduler = info.context['schedule']['scheduler']
    assert isinstance(scheduler, RequestStatement)
    statement = await scheduler()
    await nextline.reset(statement=statement)
    return True


@strawberry.type
class MutationSchedule:
    @strawberry.field
    def auto_mode(self, info: Info) -> MutationAutoMode:
        return MutationAutoMode()

    @strawberry.field
    def scheduler(self, info: Info) -> MutationScheduler:
        return MutationScheduler()

    @strawberry.mutation
    async def load_script(self, info: Info) -> bool:
        return await mutate_load_script(info)

    @strawberry.field
    def queue(self) -> MutationScheduleQueue:
        return MutationScheduleQueue()


@strawberry.type
class Mutation:
    @strawberry.field
    def schedule(self, info: Info) -> MutationSchedule:
        return MutationSchedule()
