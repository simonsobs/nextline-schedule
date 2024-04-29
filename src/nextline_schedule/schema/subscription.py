from collections.abc import AsyncIterator
from typing import cast

import strawberry
from strawberry.types import Info

from nextline_schedule.schedule import Schedule


def subscribe_auto_mode_state(info: Info) -> AsyncIterator[str]:
    schedule = cast(Schedule, info.context['schedule'])
    auto_mode = schedule.auto_mode
    r = auto_mode.subscribe_state()
    return r


@strawberry.type
class Subscription:
    schedule_auto_mode_state: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_auto_mode_state
    )
