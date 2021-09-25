import logging
from unittest.mock import patch

from django.conf import settings

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.tests.base import force_blockchain
from thenewboston_node.business_logic.tests.factories import add_blocks
from thenewboston_node.business_logic.tests.mocks.utils import patch_blockchain_states, patch_blocks

logger = logging.getLogger(__name__)

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


def yield_initialized_forced_blockchain(class_, blockchain_genesis_state, class_kwargs=None):
    blockchain = BlockchainBase.make_instance(class_, class_kwargs)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    with force_blockchain(blockchain):
        yield blockchain


@pytest.fixture
def memory_blockchain(blockchain_genesis_state):
    blockchain = MemoryBlockchain()
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain._test_treasury_account_key_pair = blockchain_genesis_state._test_treasury_account_key_pair
    blockchain.validate()
    yield blockchain


@pytest.fixture
def file_blockchain(blockchain_genesis_state, blockchain_directory):
    blockchain = FileBlockchain(
        base_directory=blockchain_directory,
        blockchain_state_storage_kwargs={
            'use_atomic_write': not settings.FASTER_UNITTESTS,
            'compressors': ('gz',)
        },
        block_chunk_storage_kwargs={
            'use_atomic_write': not settings.FASTER_UNITTESTS,
            'compressors': ('gz',)
        },
        node_signing_key=get_node_signing_key(),
    )
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain._test_treasury_account_key_pair = blockchain_genesis_state._test_treasury_account_key_pair
    blockchain.validate()
    yield blockchain


@pytest.fixture(autouse=True)  # Autouse for safety reasons
def forced_mock_blockchain(blockchain_genesis_state):
    yield from yield_initialized_forced_blockchain(MOCK_BLOCKCHAIN_CLASS, blockchain_genesis_state)


@pytest.fixture
def blockchain_base(blockchain_genesis_state):
    blockchain = BlockchainBase()
    with patch_blockchain_states(blockchain, [blockchain_genesis_state]), patch_blocks(blockchain, []):
        yield blockchain


@pytest.fixture
def file_blockchain_with_two_blockchain_states(file_blockchain, treasury_account_key_pair):
    blockchain = file_blockchain
    add_blocks(blockchain, 2, treasury_account_key_pair.private)
    blockchain.snapshot_blockchain_state()
    return blockchain


@pytest.fixture
def file_blockchain_with_three_block_chunks(file_blockchain):
    blockchain = file_blockchain
    with patch.object(blockchain, 'snapshot_period_in_blocks', 3):
        add_blocks(blockchain, 8, file_blockchain._test_treasury_account_key_pair.private)
        assert list(blockchain.get_block_chunk_storage().list_directory()) == [
            '00000000000000000000-00000000000000000002-block-chunk.msgpack',
            '00000000000000000003-00000000000000000005-block-chunk.msgpack',
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
        ]
        yield blockchain


@pytest.fixture
def file_blockchain_with_five_block_chunks(file_blockchain):
    blockchain = file_blockchain
    with patch.object(blockchain, 'snapshot_period_in_blocks', 3):
        add_blocks(blockchain, 14, file_blockchain._test_treasury_account_key_pair.private)
        assert list(blockchain.get_block_chunk_storage().list_directory()) == [
            '00000000000000000000-00000000000000000002-block-chunk.msgpack',
            '00000000000000000003-00000000000000000005-block-chunk.msgpack',
            '00000000000000000006-00000000000000000008-block-chunk.msgpack',
            '00000000000000000009-00000000000000000011-block-chunk.msgpack',
            '00000000000000000012-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
        ]
        yield blockchain
