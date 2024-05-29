import strawberry

from .auto import MutationScheduleAutoMode
from .queue import MutationScheduleQueue
from .scheduler import MutationScheduleScheduler


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


@strawberry.type
class Mutation:
    @strawberry.mutation
    def schedule(self) -> MutationSchedule:
        return MutationSchedule()
