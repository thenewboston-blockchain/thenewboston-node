from django.test import override_settings

import pytest


@pytest.fixture(autouse=True)
def unittest_settings(primary_validator_key_pair):
    with override_settings(NODE_SIGNING_KEY=primary_validator_key_pair.private, NODE_FEE_AMOUNT=4):
        yield
