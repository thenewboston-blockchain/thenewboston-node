from unittest.mock import patch

import pytest

from .base import get_file_blockchain_class


@pytest.fixture
def get_account_balance_mock():
    with patch.object(get_file_blockchain_class(), 'get_account_balance', return_value=430) as mock:
        yield mock
