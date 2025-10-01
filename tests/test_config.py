import json
from typing import TypedDict, cast

from hypothesis import HealthCheck, given, provisional, settings
from hypothesis import strategies as st
from pytest import MonkeyPatch

from nextline_schedule import Plugin
from nextlinegraphql.factory import create_app_for_test


class PluginSettings(TypedDict, total=False):
    api: str
    length_minutes: int
    policy: str
    timeout: int | float


DEFAULT = PluginSettings(
    api='https://scheduler-server.onrender.com/api/v1/schedule/',
    length_minutes=1,
    policy='{"policy": "dummy", "config": {}}',
    timeout=60,
)


def test_default() -> None:
    plugin = Plugin()
    create_app_for_test(extra_plugins=[plugin])
    assert plugin._settings.schedule == DEFAULT


def st_safe_text() -> st.SearchStrategy[str]:
    '''Safe text for environment variables'''
    return st.text(
        alphabet=st.characters(
            min_codepoint=32,  # Start from space (printable ASCII)
            max_codepoint=126,  # End at tilde (printable ASCII)
            blacklist_characters=['`', '$'],  # Shell-problematic chars
        ),
        min_size=0,
        max_size=200,
    )


def st_settings() -> st.SearchStrategy[PluginSettings]:
    return cast(
        st.SearchStrategy[PluginSettings],
        st.fixed_dictionaries(
            {},
            optional={
                'api': provisional.urls(),
                'length_minutes': st.integers(),
                'policy': st_safe_text(),
                'timeout': st.one_of(
                    st.integers(), st.floats(allow_nan=False, allow_infinity=False)
                ),
            },
        ),
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(s=st_settings())
def test_property(s: PluginSettings, monkeypatch: MonkeyPatch) -> None:
    with monkeypatch.context() as m:
        if 'api' in s:
            m.setenv('NEXTLINE_SCHEDULE__API', json.dumps(s['api']))
        if 'length_minutes' in s:
            m.setenv('NEXTLINE_SCHEDULE__LENGTH_MINUTES', f'{s["length_minutes"]}')
        if 'policy' in s:
            m.setenv('NEXTLINE_SCHEDULE__POLICY', json.dumps(s['policy']))
        if 'timeout' in s:
            m.setenv('NEXTLINE_SCHEDULE__TIMEOUT', f'{s["timeout"]}')

        plugin = Plugin()
        create_app_for_test(extra_plugins=[plugin])

        expected = {**DEFAULT, **s}
        assert plugin._settings.schedule == expected
