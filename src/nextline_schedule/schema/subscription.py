from collections.abc import AsyncIterator

import strawberry
from strawberry.types import Info

from nextline_schedule.auto import AutoMode

from .queue import ScheduleQueueItem, subscribe_schedule_queue_items


def subscribe_auto_mode_state(info: Info) -> AsyncIterator[str]:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoMode)
    r = auto_mode.subscribe_state()
    return r


@strawberry.type
class Subscription:
    schedule_auto_mode_state: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_auto_mode_state
    )

    schedule_queue_items: AsyncIterator[list[ScheduleQueueItem]] = strawberry.field(
        is_subscription=True, resolver=subscribe_schedule_queue_items
    )
