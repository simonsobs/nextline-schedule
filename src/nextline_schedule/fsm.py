from typing import Type

from transitions import Machine
from transitions.extensions import MachineFactory
from transitions.extensions.markup import HierarchicalMarkupMachine


def build_state_machine(model=None, graph=False, markup=False) -> Machine:
    '''Finite state machine.

    Diagram:
                 .-------------.
            .--->|     Off     |<--------------.
            |    '-------------'               |
            |           | turn_on()            |
         turn_off()     |                      |
            |           v                      |
            |    .-------------.               |
            |----|   Waiting   |               |
            |    '-------------'          on_raised()
            |           |                      |
            |           | on_initialized()     |
            |           | on_finished()        |
        .---------------+------------------.   |
        |   Auto        |                  |   |
        |               v                  |   |
        |        .-------------.           |   |
        |        |   Pulling   |<--.       |   |
        |        '-------------'   |       |   |
        |         run() |          |       |   |
        |               |    on_finished() |   |
        |               v          |       |   |
        |        .-------------.   |       |   |
        |        |   Running   |-----------+---'
        |        '-------------'           |
        |                                  |
        '----------------------------------'

    '''

    MachineClass: Type[Machine]
    if markup:
        MachineClass = HierarchicalMarkupMachine
    else:
        MachineClass = MachineFactory.get_predefined(
            graph=graph, nested=True, asyncio=True
        )

    # Build a state machine with nested states from dict configs with "remap"
    # in the way described in the docs:
    # https://github.com/pytransitions/transitions/tree/0.9.0#reuse-of-previously-created-hsms

    auto_state_conf = {
        'name': 'auto',
        'states': ['pulling', 'running', 'raised'],
        'transitions': [
            ['run', 'pulling', 'running'],
            ['on_finished', 'running', 'pulling'],
            ['on_raised', 'running', 'raised'],
        ],
        'initial': 'pulling',
    }

    # Ideally, we would be able to pass the auto_state_conf dict directly to
    # the MachineClass constructor, but this doesn't work with "remap."
    # Instead, we have to create a new instance of the MachineClass and pass it
    # to the parent state machine.
    auto_state = MachineClass(model=None, **auto_state_conf)  # type: ignore

    state_conf = {
        'name': 'global',
        'states': [
            'off',
            'waiting',
            {'name': 'auto', 'children': auto_state, 'remap': {'raised': 'off'}},
        ],
        'transitions': [
            ['turn_on', 'off', 'waiting'],
            ['on_initialized', 'waiting', 'auto'],
            ['on_finished', 'waiting', 'auto'],
            ['turn_off', 'waiting', 'off'],
            ['turn_off', 'auto', 'off'],
        ],
        'initial': 'off',
        'queued': True,
    }

    machine = MachineClass(model=model, **state_conf)  # type: ignore
    return machine
