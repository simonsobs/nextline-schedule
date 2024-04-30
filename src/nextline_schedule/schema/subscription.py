from collections.abc import AsyncIterator

import strawberry
from strawberry.types import Info

from nextline_schedule.auto import AutoModeStateMachine


def subscribe_auto_mode_state(info: Info) -> AsyncIterator[str]:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoModeStateMachine)
    r = auto_mode.subscribe_state()
    return r


@strawberry.type
class Subscription:
    schedule_auto_mode_state: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_auto_mode_state
    )
