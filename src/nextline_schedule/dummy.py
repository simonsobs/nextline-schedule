import random
from datetime import datetime


class DummyRequestStatement:
    '''A mock scheduler for tests.

    >>> async def main():
    ...     scheduler = DummyRequestStatement()
    ...     return await scheduler()

    >>> import asyncio
    >>> script = asyncio.run(main())
    >>> code = compile(script, '<string>', 'exec')
    >>> # exec(code, globals())

    '''

    async def __call__(self) -> str:
        return generate_dummy_statement()


def generate_dummy_statement() -> str:
    s = '\n'.join(
        f'time.sleep({random.uniform(1, 3):.2})' for _ in range(random.randint(5, 10))
    )
    s = '\n'.join(
        (
            f'# {datetime.utcnow().isoformat()}',
            'import time',
            '',
            s,
        )
    )
    return s
