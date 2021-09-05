import os
import os.path

from thenewboston_node.business_logic.blockchain.file_blockchain.block_chunk import BlockChunkFilenameMeta


def test_yield_block_chunks_meta(file_blockchain_with_three_block_chunks):
    blockchain = file_blockchain_with_three_block_chunks
    assert list(blockchain.get_block_chunk_storage().list_directory()) == [
        '00000000000000000000-00000000000000000002-block-chunk.msgpack',
        '00000000000000000003-00000000000000000005-block-chunk.msgpack',
        '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
    ]

    base_directory = blockchain.get_base_directory()
    assert list(blockchain.yield_block_chunks_meta()) == [
        BlockChunkFilenameMeta(
            absolute_file_path=os.path.join(
                base_directory,
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
            ),
            blockchain_root_relative_file_path=(
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
            ),
            storage_relative_file_path=(
                '0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
            ),
            filename='00000000000000000000-00000000000000000002-block-chunk.msgpack',
            start_block_number=0,
            end_block_number=2,
            compression=None,
            blockchain=blockchain,
        ),
        BlockChunkFilenameMeta(
            absolute_file_path=os.path.join(
                base_directory,
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
            ),
            blockchain_root_relative_file_path=(
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
            ),
            storage_relative_file_path=(
                '0/0/0/0/0/0/0/0/00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
            ),
            filename='00000000000000000003-00000000000000000005-block-chunk.msgpack',
            start_block_number=3,
            end_block_number=5,
            compression=None,
            blockchain=blockchain,
        ),
        BlockChunkFilenameMeta(
            absolute_file_path=os.path.join(
                base_directory,
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            ),
            blockchain_root_relative_file_path=(
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            ),
            storage_relative_file_path=(
                '0/0/0/0/0/0/0/0/00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            ),
            filename='00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
            start_block_number=6,
            end_block_number=7,
            compression=None,
            blockchain=blockchain,
        ),
    ]


def test_yield_block_chunks_meta_reversed(file_blockchain_with_three_block_chunks):
    blockchain = file_blockchain_with_three_block_chunks
    assert list(blockchain.get_block_chunk_storage().list_directory()) == [
        '00000000000000000000-00000000000000000002-block-chunk.msgpack',
        '00000000000000000003-00000000000000000005-block-chunk.msgpack',
        '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
    ]

    base_directory = blockchain.get_base_directory()
    assert list(blockchain.yield_block_chunks_meta(direction=-1)) == [
        BlockChunkFilenameMeta(
            absolute_file_path=os.path.join(
                base_directory,
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            ),
            blockchain_root_relative_file_path=(
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            ),
            storage_relative_file_path=(
                '0/0/0/0/0/0/0/0/00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            ),
            filename='00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
            start_block_number=6,
            end_block_number=7,
            compression=None,
            blockchain=blockchain,
        ),
        BlockChunkFilenameMeta(
            absolute_file_path=os.path.join(
                base_directory,
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
            ),
            blockchain_root_relative_file_path=(
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
            ),
            storage_relative_file_path=(
                '0/0/0/0/0/0/0/0/00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
            ),
            filename='00000000000000000003-00000000000000000005-block-chunk.msgpack',
            start_block_number=3,
            end_block_number=5,
            compression=None,
            blockchain=blockchain,
        ),
        BlockChunkFilenameMeta(
            absolute_file_path=os.path.join(
                base_directory,
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
            ),
            blockchain_root_relative_file_path=(
                'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
            ),
            storage_relative_file_path=(
                '0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
            ),
            filename='00000000000000000000-00000000000000000002-block-chunk.msgpack',
            start_block_number=0,
            end_block_number=2,
            compression=None,
            blockchain=blockchain,
        ),
    ]


def test_get_block_chunks_count(file_blockchain_with_three_block_chunks):
    blockchain = file_blockchain_with_three_block_chunks
    assert list(blockchain.get_block_chunk_storage().list_directory()) == [
        '00000000000000000000-00000000000000000002-block-chunk.msgpack',
        '00000000000000000003-00000000000000000005-block-chunk.msgpack',
        '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
    ]

    assert blockchain.get_block_chunks_count() == 3
