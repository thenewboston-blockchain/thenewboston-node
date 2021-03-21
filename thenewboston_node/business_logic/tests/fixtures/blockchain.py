from unittest.mock import patch

from django.test import override_settings

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain


@pytest.fixture
def get_head_block_mock():
    with patch.object(MockBlockchain, 'get_head_block', return_value=None) as mock:
        yield mock


@pytest.fixture
def get_next_block_number_mock():
    with patch.object(MockBlockchain, 'get_next_block_number', return_value=0) as mock:
        yield mock


@pytest.fixture
def get_next_block_identifier_mock():
    with patch.object(MockBlockchain, 'get_next_block_identifier', return_value='next-block-identifier') as mock:
        yield mock


@pytest.fixture
def get_initial_account_root_file_hash_mock():
    with patch.object(
        MockBlockchain, 'get_initial_account_root_file_hash', return_value='fake-block-identifier', create=True
    ) as mock:
        yield mock


@pytest.fixture
def get_account_balance_mock():
    with patch.object(MockBlockchain, 'get_account_balance', return_value=430) as mock:
        yield mock


@pytest.fixture
def get_account_balance_lock_mock():
    with patch.object(MockBlockchain, 'get_account_balance_lock', return_value='fake-balance-lock') as mock:
        yield mock


@pytest.fixture
def forced_memory_blockchain(initial_account_root_file):
    blockchain_settings = {
        'class': 'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain',
        'kwargs': {
            'initial_account_root_file': initial_account_root_file
        }
    }

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        yield BlockchainBase.get_instance()
    BlockchainBase.clear_instance_cache()


@pytest.fixture
def forced_mock_blockchain():
    blockchain_settings = {
        'class': 'thenewboston_node.business_logic.blockchain.mock_blockchain.MockBlockchain',
    }

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        yield BlockchainBase.get_instance()
    BlockchainBase.clear_instance_cache()
