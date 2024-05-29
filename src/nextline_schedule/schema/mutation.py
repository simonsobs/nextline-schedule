import strawberry
from strawberry.types import Info

from .auto import MutationScheduleAutoMode
from .queue import MutationScheduleQueue
from .scheduler import MutationScheduleScheduler
from .scheduler.mutation import mutate_load_script


@strawberry.type
class MutationSchedule:
    @strawberry.mutation
    def auto_mode(self) -> MutationScheduleAutoMode:
        return MutationScheduleAutoMode()

    @strawberry.mutation
    def scheduler(self) -> MutationScheduleScheduler:
        return MutationScheduleScheduler()

    @strawberry.mutation
    def queue(self) -> MutationScheduleQueue:
        return MutationScheduleQueue()

    @strawberry.mutation
    async def load_script(self, info: Info) -> bool:
        '''TODO: Deprecated. Moved to MutationScheduleScheduler.'''
        return await mutate_load_script(info)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def schedule(self) -> MutationSchedule:
        return MutationSchedule()
