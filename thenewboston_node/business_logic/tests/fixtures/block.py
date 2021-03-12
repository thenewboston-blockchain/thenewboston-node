from unittest.mock import patch

import pytest

from .base import get_file_blockchain_class


@pytest.fixture
def get_head_block_mock():
    with patch.object(get_file_blockchain_class(), 'get_head_block', return_value=None) as mock:
        yield mock


@pytest.fixture
def get_initial_account_root_file_hash_mock():
    with patch.object(
        get_file_blockchain_class(),
        'get_initial_account_root_file_hash',
        return_value='fake-block-identifier',
        create=True
    ) as mock:
        yield mock
