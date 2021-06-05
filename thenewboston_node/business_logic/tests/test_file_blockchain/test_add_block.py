from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.core.utils.cryptography import KeyPair


def test_block_chunk_is_rotated(file_blockchain_w_memory_storage, user_account, treasury_account_signing_key):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain_w_memory_storage
    file1 = '00000000000000000000-00000000000000000001-block-chunk.msgpack'
    file2 = '00000000000000000002-00000000000000000003-block-chunk.msgpack'

    with patch.object(blockchain, 'block_chunk_size', 2):
        block0 = Block.from_main_transaction(blockchain, user_account, 10, signing_key)
        blockchain.add_block(block0)

        block1 = Block.from_main_transaction(blockchain, user_account, 10, signing_key)
        blockchain.add_block(block1)

        block2 = Block.from_main_transaction(blockchain, user_account, 30, signing_key)
        blockchain.add_block(block2)

        block3 = Block.from_main_transaction(blockchain, user_account, 50, signing_key)
        blockchain.add_block(block3)

    assert blockchain.block_storage.files.keys() == {file1, file2}
    assert blockchain.block_storage.finalized == {file1, file2}


def test_block_is_appended(file_blockchain_w_memory_storage, user_account, treasury_account_signing_key):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain_w_memory_storage
    filename = '00000000000000000000-00000000000000000001-block-chunk.msgpack'

    block1 = Block.from_main_transaction(blockchain, user_account, 10, signing_key)
    blockchain.add_block(block1)
    block2 = Block.from_main_transaction(blockchain, user_account, 30, signing_key)
    blockchain.add_block(block2)

    assert blockchain.block_storage.files.keys() == {filename}
    assert blockchain.block_storage.finalized == set()


def test_cannot_add_block_twice(file_blockchain_w_memory_storage, user_account, treasury_account_signing_key):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain_w_memory_storage
    block = Block.from_main_transaction(blockchain, user_account, 10, signing_key)
    blockchain.add_block(block)

    with pytest.raises(ValidationError, match='Block number must be equal to next block number.*'):
        blockchain.add_block(block)


@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_add_block(
    blockchain_directory,
    blockchain_genesis_state,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
    primary_validator_key_pair: KeyPair,
    node_key_pair: KeyPair,
):
    blockchain = FileBlockchain(base_directory=blockchain_directory)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    treasury_account = treasury_account_key_pair.public
    treasury_initial_balance = blockchain.get_account_current_balance(treasury_account)
    assert treasury_initial_balance is not None

    user_account = user_account_key_pair.public
    pv_account = primary_validator_key_pair.public
    node_account = node_key_pair.public

    total_fees = 1 + 4

    block0 = Block.from_main_transaction(blockchain, user_account, 30, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block0)
    assert blockchain.get_account_current_balance(user_account) == 30
    assert blockchain.get_account_current_balance(treasury_account) == treasury_initial_balance - 30 - total_fees
    assert blockchain.get_account_current_balance(node_account) == 1
    assert blockchain.get_account_current_balance(pv_account) == 4

    with pytest.raises(ValidationError, match='Block number must be equal to next block number.*'):
        blockchain.add_block(block0)

    block1 = Block.from_main_transaction(blockchain, user_account, 10, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block1)
    assert blockchain.get_account_current_balance(user_account) == 40
    assert blockchain.get_account_current_balance(treasury_account
                                                  ) == (treasury_initial_balance - 30 - 10 - 2 * total_fees)
    assert blockchain.get_account_current_balance(node_account) == 1 * 2
    assert blockchain.get_account_current_balance(pv_account) == 4 * 2

    block2 = Block.from_main_transaction(blockchain, treasury_account, 5, signing_key=user_account_key_pair.private)
    blockchain.add_block(block2)
    assert blockchain.get_account_current_balance(user_account) == 40 - 5 - total_fees
    assert blockchain.get_account_current_balance(treasury_account
                                                  ) == (treasury_initial_balance - 30 - 10 + 5 - 2 * total_fees)
    assert blockchain.get_account_current_balance(node_account) == 1 * 3
    assert blockchain.get_account_current_balance(pv_account) == 4 * 3
