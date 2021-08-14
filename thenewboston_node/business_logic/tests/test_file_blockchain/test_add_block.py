import os.path
from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key


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


def test_block_chunk_is_rotated_real_file_blockchain(
    file_blockchain, user_account, treasury_account_signing_key, preferred_node
):
    blockchain = file_blockchain

    signing_key = treasury_account_signing_key
    node_signing_key = get_node_signing_key()

    with patch.object(blockchain, 'block_chunk_size', 2), patch.object(blockchain.block_storage, 'compressors', ()):
        block0 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=10,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block0)

        assert os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000000-block-chunk.msgpack'
            )
        )

        block1 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=10,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block1)

        assert not os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000000-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000001-block-chunk.msgpack'
            )
        )

        block2 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=30,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block2)

        assert not os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000000-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000001-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000002-00000000000000000002-block-chunk.msgpack'
            )
        )

        block3 = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=50,
            request_signing_key=signing_key,
            pv_signing_key=node_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block3)

        assert not os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000000-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000001-block-chunk.msgpack'
            )
        )
        assert not os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000002-00000000000000000002-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.base_directory,
                'blocks/0/0/0/0/0/0/0/0/00000000000000000002-00000000000000000003-block-chunk.msgpack'
            )
        )


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
