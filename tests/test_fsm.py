from copy import deepcopy

import pytest
from transitions import Machine
from transitions.extensions.markup import HierarchicalMarkupMachine

from nextline_schedule.fsm import build_state_machine


def test_model_default():
    machine = build_state_machine()
    assert not machine.models
    print(machine.models)


def test_model_self_literal():
    machine = build_state_machine(model=Machine.self_literal)
    assert machine.models[0] is machine
    assert len(machine.models) == 1


async def test_transitions() -> None:
    machine = build_state_machine(model=Machine.self_literal)
    await machine.start()

    # off -- turn_on --> waiting -- turn_off --> off
    assert machine.is_off()
    await machine.turn_on()
    assert machine.is_waiting()
    await machine.turn_off()

    # off -- turn_on --> waiting -- on_initialized --> auto_pulling -- turn_off --> off
    assert machine.is_off()
    await machine.turn_on()
    await machine.on_initialized()
    assert machine.is_auto_pulling()
    await machine.turn_off()

    # off -- turn_on --> waiting -- on_finished --> auto_pulling -- turn_off --> off
    assert machine.is_off()
    await machine.turn_on()
    await machine.on_finished()
    assert machine.is_auto_pulling()
    await machine.turn_off()

    # off -- turn_on --> waiting -- on_finished --> auto_pulling -- run --> auto_running -- turn_off --> off
    assert machine.is_off()
    await machine.turn_on()
    await machine.on_finished()
    await machine.run()
    assert machine.is_auto_running()
    await machine.turn_off()

    # off -- turn_on --> waiting -- on_finished --> auto_pulling -- run --> auto_running -- on_raised --> off
    assert machine.is_off()
    await machine.turn_on()
    await machine.on_finished()
    await machine.run()
    await machine.on_finished()
    assert machine.is_auto_pulling()
    await machine.run()
    assert machine.is_auto_running()
    await machine.on_raised()

    assert machine.is_off()


async def test_ignore_invalid_triggers() -> None:
    machine = build_state_machine(model=Machine.self_literal)
    await machine.start()
    assert machine.is_off()
    await machine.on_finished()  # invalid trigger

    assert machine.is_off()
    await machine.turn_on()
    await machine.on_initialized()
    assert machine.is_auto_pulling()
    await machine.on_finished()  # invalid trigger
    assert machine.is_auto_pulling()


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
