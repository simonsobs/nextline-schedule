from copy import deepcopy
from typing import Any
from unittest.mock import AsyncMock

import pytest
from hypothesis import given
from hypothesis import strategies as st
from transitions import Machine
from transitions.extensions.markup import HierarchicalMarkupMachine

from nextline_schedule.auto.state_machine.factory import build_state_machine


def test_model_default():
    machine = build_state_machine()
    assert not machine.models


def test_model_self_literal():
    machine = build_state_machine(model=Machine.self_literal)
    assert machine.models[0] is machine
    assert len(machine.models) == 1


def test_restore_from_markup():
    machine = build_state_machine(markup=True)
    assert isinstance(machine.markup, dict)
    markup = deepcopy(machine.markup)
    del markup['models']
    rebuild = HierarchicalMarkupMachine(model=None, **markup)
    assert rebuild.markup == machine.markup


@pytest.mark.skip
def test_graph():
    machine = build_state_machine(model=Machine.self_literal, graph=True)
    machine.get_graph().draw('states.png', prog='dot')


@st.composite
def st_paths(draw: st.DrawFn):
    max_n_paths = draw(st.integers(min_value=1, max_value=30))

    state_map = {
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
    final_states = {'off'}
    backwards = {'on_initialized', 'on_finished'}

    all_triggers = list({trigger for v in state_map.values() for trigger in v.keys()})

    state_map_reduced = {
        state: {trigger: v2 for trigger, v2 in v.items() if trigger not in backwards}
        for state, v in state_map.items()
    }

    paths: list[tuple[str, dict[str, Any]]] = []

    state = 'created'
    while len(paths) < max_n_paths:
        trigger_map = state_map[state]
        trigger = draw(st.sampled_from(all_triggers))
        if trigger in trigger_map:
            paths.append((trigger, trigger_map[trigger]))
            state = trigger_map[trigger]['dest']
        else:
            paths.append((trigger, {'invalid': True}))

    while state not in final_states:
        trigger_map = state_map_reduced[state]
        triggers = list(trigger_map.keys())
        trigger = draw(st.sampled_from(triggers))
        paths.append((trigger, trigger_map[trigger]))
        state = trigger_map[trigger]['dest']

    return paths


@given(paths=st_paths())
async def test_transitions_hypothesis(paths: list[tuple[str, dict[str, Any]]]):
    machine = build_state_machine(model=Machine.self_literal)
    assert machine.is_created()

    for method, map in paths:
        if map.get('invalid'):
            await getattr(machine, method)()
            continue

        if before := map.get('before'):
            setattr(machine, before, AsyncMock())

        await getattr(machine, method)()
        dest = map['dest']
        assert getattr(machine, f'is_{dest}')()

        if before:
            assert getattr(machine, before).call_count == 1
            assert getattr(machine, before).await_count == 1
