from collections.abc import AsyncIterator

import strawberry

from .auto import subscribe_auto_mode_mode, subscribe_auto_mode_state
from .queue import ScheduleQueueItem, subscribe_schedule_queue_items


@strawberry.type
class Subscription:
    schedule_auto_mode_state: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_auto_mode_state
    )

    schedule_auto_mode_mode: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_auto_mode_mode
    )

    schedule_queue_items: AsyncIterator[list[ScheduleQueueItem]] = strawberry.field(
        is_subscription=True, resolver=subscribe_schedule_queue_items
    )
