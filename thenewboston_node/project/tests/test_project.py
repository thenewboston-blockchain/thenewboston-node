import os.path

from django.conf import settings
import pytest


@pytest.mark.django_db
def test_migrations():
    pass


@pytest.mark.skipif(not os.path.isfile(settings.LOCAL_SETTINGS_PATH), reason='Local settings file does not exist')
def test_local_settings_file_applied():
    assert settings.IS_LOCAL_SETTINGS_FILE_APPLIED


@pytest.mark.skipif(
    'THENEWBOSTON_NODE_FOR_ENV_VAR_OVERRIDE_TESTING' not in os.environ, reason='Environment variable is not set'
)
def test_can_override_with_env_var():
    assert settings.FOR_ENV_VAR_OVERRIDE_TESTING == {'k': 'v'}
