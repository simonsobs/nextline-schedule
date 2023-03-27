from pathlib import Path
from types import CodeType
from typing import Any, Callable, Union

from typing_extensions import TypeAlias

Statement: TypeAlias = Union[str, Path, CodeType, Callable[[], Any]]
