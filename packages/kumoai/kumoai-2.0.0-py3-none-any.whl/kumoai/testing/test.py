import os
from typing import Callable

import pytest


def is_integration_test() -> bool:
    r"""Whether to run integration tests against a functioning development
    server.
    """
    return os.getenv('INTEGRATION_TEST', '0') == '1'


def onlyIntegrationTest(func: Callable) -> Callable:
    r"""A decorator to specify that this function belongs to the integration
    test suite.
    """
    return pytest.mark.skipif(
        not is_integration_test(),
        reason="Mock test run",
    )(func)
