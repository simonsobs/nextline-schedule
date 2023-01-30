import random


async def generate_statement(run_no: int) -> str:
    s = '\n'.join(
        f'time.sleep({random.uniform(1, 3):.2})' for _ in range(random.randint(5, 10))
    )
    s = '\n'.join(
        (
            f'# run_no: {run_no}',
            'import time',
            '',
            s,
        )
    )
    return s
