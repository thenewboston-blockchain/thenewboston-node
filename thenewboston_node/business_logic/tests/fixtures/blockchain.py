import logging
from unittest.mock import patch

from django.test import override_settings

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.utils.blockchain import generate_blockchain

LARGE_MEMORY_BLOCKCHAIN_SIZE = 100

logger = logging.getLogger(__name__)


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
def get_account_balance_mock():
    with patch.object(MockBlockchain, 'get_balance_value', return_value=430) as mock:
        yield mock


@pytest.fixture
def get_balance_lock_mock():
    with patch.object(MockBlockchain, 'get_balance_lock', return_value='fake-balance-lock') as mock:
        yield mock


@pytest.fixture
def forced_memory_blockchain(initial_account_root_file):
    blockchain_settings = {
        'class': 'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain',
        'kwargs': {
            'account_root_files': [initial_account_root_file]
        }
    }

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        yield BlockchainBase.get_instance()
    BlockchainBase.clear_instance_cache()


@pytest.fixture(autouse=True)  # Autouse for safety reasons
def forced_mock_blockchain():
    blockchain_settings = {
        'class': 'thenewboston_node.business_logic.blockchain.mock_blockchain.MockBlockchain',
        'kwargs': {}
    }

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        yield BlockchainBase.get_instance()
    BlockchainBase.clear_instance_cache()


@pytest.fixture
def large_memory_blockchain(forced_memory_blockchain, treasury_account_key_pair):
    generate_blockchain(
        forced_memory_blockchain,
        LARGE_MEMORY_BLOCKCHAIN_SIZE,
        add_initial_account_root_file=False,
        treasury_account_key_pair=treasury_account_key_pair
    )
    yield forced_memory_blockchain
