import os.path

from django.conf import settings

import pytest


@pytest.mark.django_db
def test_migrations():
    pass


@pytest.mark.skipif(not os.path.isfile(settings.LOCAL_SETTINGS_PATH), reason='Local settings file is not provided')
def test_local_settings_file_applied():
    assert settings.IS_LOCAL_SETTINGS_FILE_APPLIED


@pytest.mark.skipif('THENEWBOSTON_NODE_TEST_WITH_ENV_VARS' not in os.environ, reason='Env vars testing is not enabled')
def test_can_override_with_env_var():
    assert settings.TEST_WITH_ENV_VARS is True
