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
       turn_off()               |                      |
         |                      v                      |
         |               .-------------.               |
         |---------------|   Waiting   |          on_raised()
         |               '-------------'               |
         |                      | on_initialized()     |
         |                      | on_finished()        |
         |                      |                      |
         |   .------------------+------------------.   |
         |   |   Auto           |                  |   |
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
    ...     def on_enter_waiting(self):
    ...         print('enter the waiting state')
    ...         self.on_finished()
    ...
    ...     def on_exit_waiting(self):
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

    # Build a state machine with nested states from dict configs with "remap"
    # in the way described in the docs:
    # https://github.com/pytransitions/transitions/tree/0.9.0#reuse-of-previously-created-hsms

    auto_state_conf = {
        'name': 'auto',
        'states': ['pulling', 'running'],
        'transitions': [
            ['run', 'pulling', 'running'],
            ['on_finished', 'running', 'pulling'],
        ],
        'initial': 'pulling',
        'queued': True,
        # 'ignore_invalid_triggers': True,
    }

    # Ideally, we would be able to pass the auto_state_conf dict directly to
    # the MachineClass constructor, but this doesn't work with "remap."
    # Instead, we have to create a new instance of the MachineClass and pass it
    # to the parent state machine.
    auto_state = MachineClass(model=None, **auto_state_conf)  # type: ignore

    state_conf = {
        'name': 'global',
        'states': [
            'created',
            'off',
            'waiting',
            {'name': 'auto', 'children': auto_state},
        ],
        'transitions': [
            ['start', 'created', 'off'],
            ['turn_on', 'off', 'waiting'],
            ['on_initialized', 'waiting', 'auto'],
            ['on_finished', 'waiting', 'auto'],
            ['on_raised', 'auto', 'off'],
            {
                'trigger': 'turn_off',
                'source': ['waiting', 'auto'],
                'dest': 'off',
                'before': 'cancel_task',
            },
        ],
        'initial': 'created',
        'queued': True,
        # 'ignore_invalid_triggers': True,
    }

    machine = MachineClass(model=model, **state_conf)  # type: ignore
    return machine
