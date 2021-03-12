from django.test import override_settings

import pytest


@pytest.fixture(autouse=True)
def unittest_settings():
    with override_settings(SIGNING_KEY='46a23fd52b2690f5acf56654489fd67b3734a52f35a2b7827f5caeaa06c0c0a5'):
        yield
