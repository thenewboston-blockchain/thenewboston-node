import os
import os.path
import stat
from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.blockchain.file_blockchain.block_chunk.meta import get_block_chunk_filename_meta
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key

STAT_WRITE_PERMS_ALL = stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH


def test_get_block_chunk_file_path_meta_enhanced(
    file_blockchain: FileBlockchain, user_account, treasury_account_signing_key, preferred_node
):
    blockchain = file_blockchain

    signing_key = treasury_account_signing_key
    node_signing_key = get_node_signing_key()

    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=signing_key,
        pv_signing_key=node_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block0)

    filename = '00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
    block_chunk_file_path = os.path.join(blockchain.get_base_directory(), 'block-chunks/0/0/0/0/0/0/0/0/', filename)
    assert os.path.isfile(block_chunk_file_path)

    meta = get_block_chunk_filename_meta(filename=filename)
    assert meta
    assert meta.start_block_number == 0
    assert meta.end_block_number is None

    enhanced_meta = blockchain._get_block_chunk_file_path_meta_enhanced(filename)
    assert enhanced_meta
    assert enhanced_meta.start_block_number == 0
    assert enhanced_meta.end_block_number == 0


def test_last_block_chunk_is_properly_tracked(
    file_blockchain: FileBlockchain, user_account, treasury_account_signing_key, preferred_node
):
    blockchain = file_blockchain

    signing_key = treasury_account_signing_key
    node_signing_key = get_node_signing_key()

    assert blockchain.get_block_count() == 0

    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=signing_key,
        pv_signing_key=node_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block0)

    block_chunk_file_path = os.path.join(
        blockchain.get_base_directory(),
        'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
    )
    assert os.path.isfile(block_chunk_file_path)
    assert blockchain.get_block_count() == 1

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=signing_key,
        pv_signing_key=node_signing_key,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block1)
    assert os.path.isfile(block_chunk_file_path)
    assert blockchain.get_block_count() == 2


def test_block_chunk_is_rotated(file_blockchain, user_account, treasury_account_signing_key, preferred_node):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain
    file1 = '00000000000000000000-00000000000000000001-block-chunk.msgpack'
    file2 = '00000000000000000002-00000000000000000003-block-chunk.msgpack'
    node_signing_key = get_node_signing_key()

    with patch.object(blockchain, 'snapshot_period_in_blocks', 2):
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

    storage = blockchain.get_block_chunk_storage()
    assert list(storage.list_directory()) == [file1, file2]
    assert storage.is_finalized(file1)
    assert storage.is_finalized(file2)


def test_block_chunk_is_rotated_real_file_blockchain(
    file_blockchain, user_account, treasury_account_signing_key, preferred_node
):
    blockchain = file_blockchain

    signing_key = treasury_account_signing_key
    node_signing_key = get_node_signing_key()

    with (
        patch.object(blockchain, 'snapshot_period_in_blocks',
                     2), patch.object(blockchain.get_block_chunk_storage(), 'compressors', ())
    ):
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
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
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
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            )
        )
        final_filename = os.path.join(
            blockchain.get_base_directory(),
            'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000001-block-chunk.msgpack'
        )
        assert os.path.isfile(final_filename)
        assert not bool(os.stat(final_filename).st_mode & STAT_WRITE_PERMS_ALL)

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
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000001-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000002-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
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
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000001-block-chunk.msgpack'
            )
        )
        assert not os.path.isfile(
            os.path.join(
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000002-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            )
        )
        assert os.path.isfile(
            os.path.join(
                blockchain.get_base_directory(),
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000002-00000000000000000003-block-chunk.msgpack'
            )
        )


def test_block_appended(file_blockchain, user_account, treasury_account_signing_key, preferred_node):
    signing_key = treasury_account_signing_key
    blockchain = file_blockchain
    filename = '00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'

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

    storage = blockchain.get_block_chunk_storage()
    assert list(storage.list_directory()) == [filename]
    assert not storage.is_finalized(filename)


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
