from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from transitions import Machine
from transitions.extensions import HierarchicalAsyncGraphMachine
from transitions.extensions.asyncio import HierarchicalAsyncMachine
from transitions.extensions.markup import HierarchicalMarkupMachine

from nextline_schedule.auto.state_machine.config import CONFIG

SELF_LITERAL = Machine.self_literal


def test_model_default() -> None:
    machine = HierarchicalAsyncMachine(model=None, **CONFIG)  # type: ignore
    assert not machine.models


def test_model_self_literal() -> None:
    machine = HierarchicalAsyncMachine(model=SELF_LITERAL, **CONFIG)  # type: ignore
    assert machine.models[0] is machine
    assert len(machine.models) == 1


def test_restore_from_markup() -> None:
    machine = HierarchicalMarkupMachine(model=None, **CONFIG)  # type: ignore
    assert isinstance(machine.markup, dict)
    markup = deepcopy(machine.markup)
    del markup['models']  # type: ignore
    rebuild = HierarchicalMarkupMachine(model=None, **markup)  # type: ignore
    assert rebuild.markup == machine.markup


@pytest.mark.skip
def test_graph(tmp_path: Path) -> None:  # pragma: no cover
    FILE_NAME = 'states.png'
    path = tmp_path / FILE_NAME
    # print(f'Saving the state diagram to {path}...')
    machine = HierarchicalAsyncGraphMachine(model=SELF_LITERAL, **CONFIG)  # type: ignore
    machine.get_graph().draw(path, prog='dot')


STATE_MAP = {
    'created': {
        'start': {'dest': 'off'},
    },
    'off': {
        'turn_on': {'dest': 'auto_waiting'},
    },
    'auto_waiting': {
        'turn_off': {'dest': 'off', 'before': 'cancel_task'},
        'on_initialized': {'dest': 'auto_pulling'},
        'on_finished': {'dest': 'auto_pulling'},
        'on_raised': {'dest': 'off'},
    },
    'auto_pulling': {
        'run': {'dest': 'auto_running'},
        'turn_off': {'dest': 'off', 'before': 'cancel_task'},
        'on_raised': {'dest': 'off'},
    },
    'auto_running': {
        'on_finished': {'dest': 'auto_pulling'},
        'turn_off': {'dest': 'off', 'before': 'cancel_task'},
        'on_raised': {'dest': 'off'},
    },
}

TRIGGERS = list({trigger for v in STATE_MAP.values() for trigger in v.keys()})


@settings(max_examples=200)
@given(triggers=st.lists(st.sampled_from(TRIGGERS)))
async def test_transitions(triggers: list[str]) -> None:
    machine = HierarchicalAsyncMachine(model=SELF_LITERAL, **CONFIG)  # type: ignore
    assert machine.is_created()

    for trigger in triggers:
        prev = machine.state
        if (map_ := STATE_MAP[prev].get(trigger)) is None:
            await getattr(machine, trigger)()
            assert machine.state == prev
            continue

        if before := map_.get('before'):
            setattr(machine, before, AsyncMock())

        assert await getattr(machine, trigger)() is True
        dest = map_['dest']
        assert getattr(machine, f'is_{dest}')()

        if before:
            assert getattr(machine, before).call_count == 1
            assert getattr(machine, before).await_count == 1
