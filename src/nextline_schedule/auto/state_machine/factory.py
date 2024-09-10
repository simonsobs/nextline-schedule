'''The configuration of the finite state machine of the auto mode states.

The package "transitions" is used: https://github.com/pytransitions/transitions

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

>>> from transitions.extensions import HierarchicalMachine

>>> model = Model()
>>> machine = HierarchicalMachine(model=model, **CONFIG)
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


from typing import Type

from transitions import Machine
from transitions.extensions import MachineFactory
from transitions.extensions.markup import HierarchicalMarkupMachine

AUTO_STATE_CONFIG = {
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

CONFIG = {
    'name': 'global',
    'states': ['created', 'off', AUTO_STATE_CONFIG],
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


def build_state_machine(model=None, graph=False, asyncio=True, markup=False) -> Machine:
    MachineClass: Type[Machine]
    if markup:
        MachineClass = HierarchicalMarkupMachine
    else:
        MachineClass = MachineFactory.get_predefined(
            graph=graph, nested=True, asyncio=asyncio
        )

    machine = MachineClass(model=model, **CONFIG)  # type: ignore
    return machine
