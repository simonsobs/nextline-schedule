from nextline import Nextline
from .funcs import generate_statement


def DummyRequestStatement(nextline: Nextline):
    async def f() -> str:
        return generate_statement(run_no=nextline.run_no + 1)
    return f
