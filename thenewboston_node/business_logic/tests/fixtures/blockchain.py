import logging
from unittest.mock import patch

from django.test import override_settings

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.tests.factories import add_blocks_to_blockchain

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


def yield_forced_blockchain(class_, initial_account_root_file, class_kwargs=None):
    blockchain_settings = {'class': class_, 'kwargs': class_kwargs or {}}

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        blockchain = BlockchainBase.get_instance()
        blockchain.add_account_root_file(initial_account_root_file)
        blockchain.validate()
        yield blockchain
    BlockchainBase.clear_instance_cache()


@pytest.fixture
def forced_memory_blockchain(initial_account_root_file):
    yield from yield_forced_blockchain(
        'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain',
        initial_account_root_file,
    )


@pytest.fixture
def forced_file_blockchain(initial_account_root_file, blockchain_directory):
    yield from yield_forced_blockchain(
        'thenewboston_node.business_logic.blockchain.file_blockchain.FileBlockchain',
        initial_account_root_file,
        class_kwargs={
            'base_directory': blockchain_directory,
        }
    )


@pytest.fixture(autouse=True)  # Autouse for safety reasons
def forced_mock_blockchain(initial_account_root_file):
    yield from yield_forced_blockchain(
        'thenewboston_node.business_logic.blockchain.mock_blockchain.MockBlockchain', initial_account_root_file
    )


@pytest.fixture
def large_blockchain(treasury_account_key_pair):
    blockchain = BlockchainBase.get_instance()

    accounts = blockchain.get_first_account_root_file().accounts
    assert len(accounts) == 1
    treasury_account, account_balance = list(accounts.items())[0]
    assert treasury_account_key_pair.public == treasury_account
    assert account_balance.value > 10000000000  # tons of money present

    add_blocks_to_blockchain(blockchain, 100, treasury_account_key_pair.private)
    yield blockchain
