from typing import Optional

import strawberry
from nextline import Nextline
from strawberry.types import Info

from nextline_schedule.scheduler import Scheduler


@strawberry.input
class MutationSchedulerUpdateInput:
    api_url: Optional[str] = None
    length_minutes: Optional[int] = None
    policy: Optional[str] = None


def mutate_update(info: Info, input: MutationSchedulerUpdateInput) -> bool:
    scheduler = info.context['schedule']['scheduler']
    assert isinstance(scheduler, Scheduler)
    if input.api_url is not None:
        scheduler._api_url = input.api_url
    if input.length_minutes is not None:
        scheduler._length_minutes = input.length_minutes
    if input.policy is not None:
        scheduler._policy = input.policy
    return True


async def mutate_load_script(info: Info) -> bool:
    nextline = info.context["nextline"]
    assert isinstance(nextline, Nextline)
    scheduler = info.context['schedule']['scheduler']
    assert callable(scheduler)
    statement = await scheduler()
    assert isinstance(statement, str)
    await nextline.reset(statement=statement)
    return True


@strawberry.type
class MutationScheduleScheduler:
    update: bool = strawberry.mutation(resolver=mutate_update)
    load_script: bool = strawberry.mutation(resolver=mutate_load_script)
