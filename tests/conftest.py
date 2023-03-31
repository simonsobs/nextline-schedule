import sys

import pytest

if not sys.version_info >= (3, 9):
    from nextline.test import suppress_atexit_oserror

    _ = pytest.fixture(scope='session', autouse=True)(suppress_atexit_oserror)
