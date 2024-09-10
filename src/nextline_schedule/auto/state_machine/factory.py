from typing import Type

from transitions import Machine
from transitions.extensions import MachineFactory
from transitions.extensions.markup import HierarchicalMarkupMachine


def build_state_machine(model=None, graph=False, asyncio=True, markup=False) -> Machine:
    '''Finite state machine for the auto-pilot mode states.

    State Diagram:

                         .-------------.
                         |   Created   |
                         '-------------'
                                | start()
                                |
                                v
                         .-------------.
         .-------------->|     Off     |<--------------.
         |               '-------------'               |
         |                      | turn_on()            |
       turn_off()               |                 on_raised()
         |                      |                      |
         |                      |                      |
         |   .------------------+------------------.   |
         |   |   Auto           |                  |   |
         |   |                  v                  |   |
         |   |           .-------------.           |   |
         |   |           |   Waiting   |           |   |
         |   |           '-------------'           |   |
         |   |                  | on_initialized() |   |
         |   |                  | on_finished()    |   |
         |   |                  v                  |   |
         |   |           .-------------.           |   |
         |   |           |   Pulling   |           |   |
         '---|           '-------------'           |---'
             |         run() |     ^               |
             |               |     |               |
             |               v     | on_finished() |
             |           .-------------.           |
             |           |   Running   |           |
             |           '-------------'           |
             |                                     |
             '-------------------------------------'

    >>> class Model:
    ...     def on_enter_auto_waiting(self):
    ...         print('enter the waiting state')
    ...         self.on_finished()
    ...
    ...     def on_exit_auto_waiting(self):
    ...        print('exit the waiting state')
    ...
    ...     def on_enter_auto_pulling(self):
    ...        print('enter the pulling state')

    >>> model = Model()
    >>> machine = build_state_machine(model=model, asyncio=False)
    >>> model.state
    'created'

    >>> _ = model.start()
    >>> model.state
    'off'

    >>> _ = model.turn_on()
    enter the waiting state
    exit the waiting state
    enter the pulling state

    >>> model.state
    'auto_pulling'


    '''

    MachineClass: Type[Machine]
    if markup:
        MachineClass = HierarchicalMarkupMachine
    else:
        MachineClass = MachineFactory.get_predefined(
            graph=graph, nested=True, asyncio=asyncio
        )

    auto_state_conf = {
        'name': 'auto',
        'children': ['waiting', 'pulling', 'running'],
        'initial': 'waiting',
        'transitions': [
            ['on_initialized', 'waiting', 'pulling'],
            ['on_finished', 'waiting', 'pulling'],
            ['run', 'pulling', 'running'],
            ['on_finished', 'running', 'pulling'],
        ],
    }

    state_conf = {
        'name': 'global',
        'states': ['created', 'off', auto_state_conf],
        'transitions': [
            ['start', 'created', 'off'],
            ['turn_on', 'off', 'auto'],
            ['on_raised', 'auto', 'off'],
            {
                'trigger': 'turn_off',
                'source': 'auto',
                'dest': 'off',
                'before': 'cancel_task',
            },
        ],
        'initial': 'created',
        'queued': True,
        'ignore_invalid_triggers': True,
    }

    machine = MachineClass(model=model, **state_conf)  # type: ignore
    return machine
