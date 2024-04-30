import strawberry
from strawberry.types import Info

from nextline_schedule.queue import PushArg, Queue

from .types import QueryScheduleQueueItem


@strawberry.input
class ScheduleQueueAddItemInput:
    name: str
    script: str

    def to_push_arg(self) -> PushArg:
        return PushArg(
            name=self.name,
            script=self.script,
        )


def mutate_push(info: Info, input: ScheduleQueueAddItemInput) -> QueryScheduleQueueItem:
    queue = info.context['schedule']['queue']
    assert isinstance(queue, Queue)
    push_arg = input.to_push_arg()
    item = queue.push(push_arg)
    return QueryScheduleQueueItem.from_(item)


@strawberry.type
class MutationScheduleQueue:
    push: QueryScheduleQueueItem = strawberry.field(resolver=mutate_push)
