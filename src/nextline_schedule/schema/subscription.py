from typing import AsyncIterator

import strawberry
from strawberry.types import Info


def subscribe_auto_mode_state(info: Info) -> AsyncIterator[str]:
    auto_mode = info.context['auto_mode']
    r = auto_mode.subscribe_state()
    return r


@strawberry.type
class Subscription:
    schedule_auto_mode_state: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_auto_mode_state
    )
