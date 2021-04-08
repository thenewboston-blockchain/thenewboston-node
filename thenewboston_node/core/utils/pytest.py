import os
import sys

from .misc import yaml_coerce

PYTEST_RUN_SLOW_TESTS = 'PYTEST_RUN_SLOW_TESTS'


def is_pytest_running():
    # TODO(dmu) HIGH: Implement a better way of detecting pytest
    return os.getenv('PYTEST_RUNNING') == 'true' or os.path.basename(sys.argv[0]) in ('pytest', 'py.test')


def should_run(skip_name):
    return bool(yaml_coerce(os.getenv(skip_name)))


def skip_slow(wrapped):
    import pytest  # because pytest is a dev dependency
    return pytest.mark.skipif(not should_run(PYTEST_RUN_SLOW_TESTS), reason='Slow')(wrapped)
