import asyncio
import random
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import httpx
from nextline import Nextline
from rich import print


@asynccontextmanager
async def schedule(nextline: Nextline):
    task = asyncio.gather(
        subscribe_run_info(nextline),
        subscribe_prompt_info(nextline),
    )
    try:
        yield
    finally:
        await task


async def subscribe_run_info(nextline: Nextline):
    async for run_info in nextline.subscribe_run_info():
        print(run_info)
        if run_info.state == 'finished':
            break

    await asyncio.sleep(1)

    while True:
        # statement = await generate_statement(nextline.run_no + 1)
        statement = await pull_from_scheduler()
        await nextline.reset(statement=statement)
        await asyncio.sleep(1)
        await nextline.run()


async def subscribe_prompt_info(nextline: Nextline):
    async for prompt_info in nextline.subscribe_prompt_info():
        if prompt_info.trace_call_end:  # TODO: remove when unnecessary
            continue
        if not prompt_info.open:
            continue
        nextline.send_pdb_command(
            command='continue',
            prompt_no=prompt_info.prompt_no,
            trace_no=prompt_info.trace_no,
        )


async def pull_from_scheduler():

    # https://github.com/simonsobs/so-scheduler/blob/master/readme.md#schedule-api
    API_URL = 'https://scheduler-uobd.onrender.com/api/v1/schedule/'

    t0 = datetime.utcnow()
    minutes = random.randint(1, 2)
    duration = timedelta(minutes=minutes)
    t1 = t0 + duration
    t0_fmt = t0.strftime('%Y-%m-%d %H:%M')
    t1_fmt = t1.strftime('%Y-%m-%d %H:%M')
    data = {"t0": t0_fmt, "t1": t1_fmt, "policy": "dummy"}
    print(data)
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=data)
    print(response.json())
    return response.json()['commands']
