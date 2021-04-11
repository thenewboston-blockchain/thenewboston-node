import logging
import os
from pathlib import Path

from split_settings.tools import include, optional

from thenewboston_node.core.utils.pytest import is_pytest_running

# Build paths inside the project like this: BASE_DIR / 'subdir'.
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENVVAR_SETTINGS_PREFIX = 'THENEWBOSTON_NODE_'

local_settings_path_base = os.getenv(f'{ENVVAR_SETTINGS_PREFIX}SETTINGS', 'local/settings')
if is_pytest_running():
    # We use dedicated local settings here to have reproducible unittest runs
    LOCAL_SETTINGS_PATH = str(ROOT_DIR / (local_settings_path_base + '.unittests.py'))
    overriding_settings = (optional(LOCAL_SETTINGS_PATH),)
    if os.getenv('THENEWBOSTON_NODE_TEST_WITH_ENV_VARS') == 'true':
        overriding_settings += ('envvars.py',)  # type: ignore
else:
    LOCAL_SETTINGS_PATH = str(ROOT_DIR / (local_settings_path_base + '.py'))
    overriding_settings = (optional(LOCAL_SETTINGS_PATH), 'envvars.py')  # type: ignore

include(*(
    'base.py',
    'logging.py',
    'custom.py',
) + overriding_settings + ('sentry.py', 'docker.py'))

logging.captureWarnings(True)

assert SECRET_KEY is not NotImplemented  # type: ignore # noqa: F821
