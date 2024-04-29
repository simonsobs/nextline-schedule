import dataclasses

from .auto import AutoModeStateMachine
from .scheduler import RequestStatement


@dataclasses.dataclass
class Schedule:
    auto_mode: AutoModeStateMachine
    scheduler: RequestStatement
