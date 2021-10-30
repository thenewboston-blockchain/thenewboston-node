from functools import partial

from django.core.management import call_command

import pytest


@pytest.fixture
def blockchain_management_command():
    return partial(call_command, 'blockchain')
