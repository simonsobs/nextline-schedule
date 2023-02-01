from nextline import Nextline
from .funcs import generate_statement


class DummyRequestStatement:
    def __init__(self, nextline: Nextline):
        self._nextline = nextline

    async def __call__(self) -> str:
        return generate_statement(run_no=self._nextline.run_no + 1)
