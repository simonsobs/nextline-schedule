import strawberry
from strawberry.types import Info

from nextline_schedule.queue import PushArg, Queue

from .types import ScheduleQueueItem


@strawberry.input
class ScheduleQueuePushInput:
    name: str
    script: str

    def to_push_arg(self) -> PushArg:
        return PushArg(
            name=self.name,
            script=self.script,
        )


async def mutate_push(info: Info, input: ScheduleQueuePushInput) -> ScheduleQueueItem:
    queue = info.context['schedule']['queue']
    assert isinstance(queue, Queue)
    push_arg = input.to_push_arg()
    item = await queue.push(push_arg)
    return ScheduleQueueItem.from_(item)


async def mutate_remove(info: Info, id: int) -> bool:
    queue = info.context['schedule']['queue']
    assert isinstance(queue, Queue)
    return await queue.remove(id)


@strawberry.type
class MutationScheduleQueue:
    push: ScheduleQueueItem = strawberry.mutation(resolver=mutate_push)
    remove: bool = strawberry.mutation(resolver=mutate_remove)
