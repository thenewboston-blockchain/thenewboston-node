from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.cryptography import KeyPair, derive_public_key


def test_block_chunk_is_rotated(
    file_blockchain_w_memory_storage, user_account, treasury_account_signing_key, preferred_node
):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain_w_memory_storage
    file1 = '00000000000000000000-00000000000000000001-block-chunk.msgpack'
    file2 = '00000000000000000002-00000000000000000003-block-chunk.msgpack'
    node_signing_key = get_node_signing_key()

    with patch.object(blockchain, 'block_chunk_size', 2):
        block0 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=10,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block0)

        block1 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=10,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block1)

        block2 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=30,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block2)

        block3 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=50,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block3)

    assert blockchain.block_storage.files.keys() == {file1, file2}
    assert blockchain.block_storage.finalized == {file1, file2}


def test_block_is_appended(
    file_blockchain_w_memory_storage, user_account, treasury_account_signing_key, preferred_node
):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain_w_memory_storage
    filename = '00000000000000000000-00000000000000000001-block-chunk.msgpack'

    node_signing_key = get_node_signing_key()

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=signing_key,
        pv_signing_key=node_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block1)

    block2 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=30,
        request_signing_key=signing_key,
        pv_signing_key=node_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block2)

    assert blockchain.block_storage.files.keys() == {filename}
    assert blockchain.block_storage.finalized == set()


def test_cannot_add_block_twice(
    file_blockchain_w_memory_storage, user_account, treasury_account_signing_key, preferred_node
):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain_w_memory_storage

    node_signing_key = get_node_signing_key()
    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=signing_key,
        pv_signing_key=node_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block)

    with pytest.raises(ValidationError, match='Block number must be equal to next block number.*'):
        blockchain.add_block(block)


def test_can_add_block(
    file_blockchain,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
    preferred_node,
):
    blockchain = file_blockchain

    treasury_account_number = treasury_account_key_pair.public
    treasury_initial_balance = blockchain.get_account_current_balance(treasury_account_number)
    assert treasury_initial_balance is not None

    user_account_number = user_account_key_pair.public
    primary_validator = blockchain.get_primary_validator()
    assert primary_validator
    pv_account_number = primary_validator.identifier
    assert pv_account_number
    preferred_node_account_number = preferred_node.identifier

    assert primary_validator.fee_amount > 0
    assert preferred_node.fee_amount > 0
    assert primary_validator.fee_amount != preferred_node.fee_amount
    total_fees = primary_validator.fee_amount + preferred_node.fee_amount

    pv_signing_key = get_node_signing_key()
    assert derive_public_key(pv_signing_key) == pv_account_number
    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account_number,
        amount=30,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=pv_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block0)
    assert blockchain.get_account_current_balance(user_account_number) == 30
    assert blockchain.get_account_current_balance(
        treasury_account_number
    ) == treasury_initial_balance - 30 - total_fees
    assert blockchain.get_account_current_balance(preferred_node_account_number) == preferred_node.fee_amount
    assert blockchain.get_account_current_balance(pv_account_number) == primary_validator.fee_amount

    with pytest.raises(ValidationError, match='Block number must be equal to next block number.*'):
        blockchain.add_block(block0)

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account_number,
        amount=10,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=pv_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block1)
    assert blockchain.get_account_current_balance(user_account_number) == 40
    assert blockchain.get_account_current_balance(treasury_account_number
                                                  ) == (treasury_initial_balance - 30 - 10 - 2 * total_fees)
    assert blockchain.get_account_current_balance(preferred_node_account_number) == preferred_node.fee_amount * 2
    assert blockchain.get_account_current_balance(pv_account_number) == primary_validator.fee_amount * 2

    block2 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=treasury_account_number,
        amount=5,
        request_signing_key=user_account_key_pair.private,
        pv_signing_key=pv_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block2)
    assert blockchain.get_account_current_balance(user_account_number) == 40 - 5 - total_fees
    assert blockchain.get_account_current_balance(treasury_account_number
                                                  ) == (treasury_initial_balance - 30 - 10 + 5 - 2 * total_fees)
    assert blockchain.get_account_current_balance(preferred_node_account_number) == preferred_node.fee_amount * 3
    assert blockchain.get_account_current_balance(pv_account_number) == primary_validator.fee_amount * 3
