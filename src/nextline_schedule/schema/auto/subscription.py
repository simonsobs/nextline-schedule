from collections.abc import AsyncIterator

from strawberry.types import Info

from nextline_schedule.auto import AutoMode


def subscribe_auto_mode_state(info: Info) -> AsyncIterator[str]:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoMode)
    return auto_mode.subscribe_state()


def subscribe_auto_mode_mode(info: Info) -> AsyncIterator[str]:
    auto_mode = info.context['schedule']['auto_mode']
    assert isinstance(auto_mode, AutoMode)
    return auto_mode.subscribe_mode()
