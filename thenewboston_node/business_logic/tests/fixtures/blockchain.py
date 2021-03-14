from unittest.mock import patch

from django.test import override_settings

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase

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


@pytest.fixture
def get_account_balance_mock():
    with patch.object(get_file_blockchain_class(), 'get_account_balance', return_value=430) as mock:
        yield mock


@pytest.fixture
def initial_account_root_file(initial_account_keys):
    account = initial_account_keys[1]
    return {
        account: {
            'balance': 281474976710656,
            'balance_lock': account,
        }
    }


@pytest.fixture
def use_memory_blockchain(initial_account_root_file):
    blockchain_settings = {
        'class': 'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain',
        'kwargs': {
            'initial_account_root_file': initial_account_root_file
        }
    }

    BlockchainBase._instance = None

    with override_settings(BLOCKCHAIN=blockchain_settings):
        yield

    BlockchainBase._instance = None
