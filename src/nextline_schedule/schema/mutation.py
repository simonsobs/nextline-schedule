from typing import Optional

import strawberry
from nextline import Nextline
from strawberry.types import Info

from nextline_schedule.scheduler import Scheduler

from .auto import MutationScheduleAutoMode
from .queue import MutationScheduleQueue


@strawberry.input
class MutationSchedulerInput:
    api_url: Optional[str] = None
    length_minutes: Optional[int] = None
    policy: Optional[str] = None


async def mutate_load_script(info: Info) -> bool:
    nextline = info.context["nextline"]
    assert isinstance(nextline, Nextline)
    scheduler = info.context['schedule']['scheduler']
    assert callable(scheduler)
    statement = await scheduler()
    assert isinstance(statement, str)
    await nextline.reset(statement=statement)
    return True


def mutate_update(info: Info, input: MutationSchedulerInput) -> bool:
    scheduler = info.context['schedule']['scheduler']
    assert isinstance(scheduler, Scheduler)
    if input.api_url is not None:
        scheduler._api_url = input.api_url
    if input.length_minutes is not None:
        scheduler._length_minutes = input.length_minutes
    if input.policy is not None:
        scheduler._policy = input.policy
    return True


@strawberry.type
class MutationScheduler:
    update: bool = strawberry.mutation(resolver=mutate_update)
    load_script: bool = strawberry.mutation(resolver=mutate_load_script)


@strawberry.type
class MutationSchedule:
    @strawberry.field
    def auto_mode(self) -> MutationScheduleAutoMode:
        return MutationScheduleAutoMode()

    @strawberry.field
    def scheduler(self) -> MutationScheduler:
        return MutationScheduler()

    @strawberry.mutation
    async def load_script(self, info: Info) -> bool:
        '''TODO: Deprecated. Moved to MutationScheduleScheduler.'''
        return await mutate_load_script(info)

    @strawberry.field
    def queue(self) -> MutationScheduleQueue:
        return MutationScheduleQueue()


@strawberry.type
class Mutation:
    @strawberry.field
    def schedule(self) -> MutationSchedule:
        return MutationSchedule()
