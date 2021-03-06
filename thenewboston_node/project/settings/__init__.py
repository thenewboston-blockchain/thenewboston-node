import os
from pathlib import Path

from split_settings.tools import include
from split_settings.tools import optional

from thenewboston_node.core.utils.pytest import is_pytest_running

# Build paths inside the project like this: BASE_DIR / 'subdir'.
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENVVAR_SETTINGS_PREFIX = 'THENEWBOSTON_NODE_'

local_settings_path_base = os.getenv(f'{ENVVAR_SETTINGS_PREFIX}SETTINGS', 'local/settings')
if is_pytest_running():
    LOCAL_SETTINGS_PATH = str(ROOT_DIR / (local_settings_path_base + '.unittests.py'))
    overriding_settings = (optional(LOCAL_SETTINGS_PATH),)
else:
    LOCAL_SETTINGS_PATH = str(ROOT_DIR / (local_settings_path_base + '.py'))
    overriding_settings = (optional(LOCAL_SETTINGS_PATH), 'envvars.py')

include(*(
    'base.py',
    'logging.py',
    'custom.py',
) + overriding_settings + ('sentry.py',))

assert SECRET_KEY is not NotImplemented  # noqa: F821
