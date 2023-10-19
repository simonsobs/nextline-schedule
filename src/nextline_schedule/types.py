from pathlib import Path
from types import CodeType
from typing import Any, Callable

Statement = str | Path | CodeType | Callable[[], Any]
