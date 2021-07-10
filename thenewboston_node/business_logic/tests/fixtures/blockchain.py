import logging
from unittest.mock import patch

from django.test import override_settings

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.tests.factories import add_blocks_to_blockchain
from thenewboston_node.business_logic.tests.mocks.storage_mock import StorageMock
from thenewboston_node.business_logic.utils.iter import get_generator

logger = logging.getLogger(__name__)

LARGE_MEMORY_BLOCKCHAIN_SIZE = 100

MEMORY_BLOCKCHAIN_CLASS = 'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain'
FILE_BLOCKCHAIN_CLASS = 'thenewboston_node.business_logic.blockchain.file_blockchain.FileBlockchain'
MOCK_BLOCKCHAIN_CLASS = 'thenewboston_node.business_logic.blockchain.mock_blockchain.MockBlockchain'


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
def get_account_state_mock():
    with patch.object(MockBlockchain, 'get_account_balance', return_value=430) as mock:
        yield mock


@pytest.fixture
def get_account_lock_mock():
    with patch.object(MockBlockchain, 'get_account_balance_lock', return_value='fake-balance-lock') as mock:
        yield mock


def yield_forced_blockchain(class_, class_kwargs=None):
    blockchain_settings = {'class': class_, 'kwargs': class_kwargs or {}}

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        blockchain = BlockchainBase.get_instance()
        yield blockchain
    BlockchainBase.clear_instance_cache()


def yield_and_init_forced_blockchain(class_, blockchain_genesis_state, class_kwargs=None):
    blockchain = next(yield_forced_blockchain(class_, class_kwargs))
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()
    yield blockchain


@pytest.fixture
def memory_blockchain(blockchain_genesis_state):
    blockchain = MemoryBlockchain()
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()
    yield blockchain


@pytest.fixture
def forced_memory_blockchain(blockchain_genesis_state):
    yield from yield_and_init_forced_blockchain(MEMORY_BLOCKCHAIN_CLASS, blockchain_genesis_state)


@pytest.fixture
def forced_file_blockchain(blockchain_genesis_state, blockchain_directory):
    yield from yield_and_init_forced_blockchain(
        FILE_BLOCKCHAIN_CLASS, blockchain_genesis_state, class_kwargs={'base_directory': blockchain_directory}
    )


@pytest.fixture(autouse=True)  # Autouse for safety reasons
def forced_mock_blockchain(blockchain_genesis_state):
    yield from yield_and_init_forced_blockchain(MOCK_BLOCKCHAIN_CLASS, blockchain_genesis_state)


@pytest.fixture
def large_blockchain(treasury_account_key_pair):
    blockchain = BlockchainBase.get_instance()

    accounts = blockchain.get_first_blockchain_state().account_states
    assert len(accounts) == 1
    treasury_account, account_state = list(accounts.items())[0]
    assert treasury_account_key_pair.public == treasury_account
    assert account_state.balance > 10000000000  # tons of money present

    add_blocks_to_blockchain(blockchain, 100, treasury_account_key_pair.private)
    yield blockchain


@pytest.fixture
def file_blockchain_w_memory_storage(
    forced_file_blockchain, blockchain_genesis_state, forced_mock_network, get_primary_validator_mock,
    get_preferred_node_mock
):
    block_storage_mock = patch.object(forced_file_blockchain, 'block_storage', StorageMock())
    arf_storage_mock = patch.object(forced_file_blockchain, 'blockchain_states_storage', StorageMock())

    with block_storage_mock, arf_storage_mock:
        forced_file_blockchain.add_blockchain_state(blockchain_genesis_state)
        forced_file_blockchain.validate()
        yield forced_file_blockchain


@pytest.fixture
def blockchain_base(blockchain_genesis_state):
    blockchain = BlockchainBase()
    with patch.object(blockchain, 'yield_blockchain_states', get_generator([blockchain_genesis_state])):
        yield blockchain
