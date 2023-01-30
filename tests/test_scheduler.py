from nextline_schedule.impl import pull_from_scheduler


async def test_one():

    script = await pull_from_scheduler()
    assert script
