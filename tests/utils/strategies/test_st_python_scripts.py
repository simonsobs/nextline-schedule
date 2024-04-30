import pytest
from hypothesis import HealthCheck, given, settings

from nextline_schedule.utils.strategies import st_python_scripts


@given(st_python_scripts())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_one(capsys: pytest.CaptureFixture, script: str) -> None:
    exec(script, globals())
    capsys.readouterr()  # clear
