import os.path
from unittest.mock import patch

from thenewboston_node.business_logic.blockchain.file_blockchain.base import (
    FileBlockchain, get_block_chunk_filename_meta, get_blockchain_state_filename_meta
)
from thenewboston_node.business_logic.tests.factories import add_blocks_to_blockchain


def test_get_block_chunk_filename_meta():
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack') == (12, 101, None)
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.xz') == (12, 101, 'xz')
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.bz2') == (12, 101, 'bz2')
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.gz') == (12, 101, 'gz')
    assert get_block_chunk_filename_meta('00012-xxxxxx-block-chunk.msgpack.gz') == (12, None, 'gz')
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.zip') is None
    assert get_block_chunk_filename_meta('00012-abc-block-chunk.msgpack') is None
    assert get_block_chunk_filename_meta('00012-000101-aaaaa.msgpack') is None


def test_get_blockchain_filename_meta():
    assert get_blockchain_state_filename_meta('0000012-blockchain-state.msgpack') == (12, None)
    assert get_blockchain_state_filename_meta('000000!-blockchain-state.msgpack') == (None, None)
    assert get_blockchain_state_filename_meta('0000001-blockchain-state.msgpack.xz') == (1, 'xz')
    assert get_blockchain_state_filename_meta('0000002-blockchain-state.msgpack.bz2') == (2, 'bz2')
    assert get_blockchain_state_filename_meta('0000003-blockchain-state.msgpack.gz') == (3, 'gz')
    assert get_blockchain_state_filename_meta('000aaaa-blockchain-state.msgpack') is None
    assert get_blockchain_state_filename_meta('0000012-aaa.msgpack') is None
    assert get_blockchain_state_filename_meta('0000012-blockchain-state.msgpack.zip') is None


def test_file_blockchain_blocks_contain_metadata(file_blockchain: FileBlockchain, treasury_account_key_pair):
    blockchain = file_blockchain
    with patch.object(blockchain, 'block_chunk_size', 4), patch.object(blockchain.block_storage, 'compressors', ()):
        add_blocks_to_blockchain(blockchain, 10, treasury_account_key_pair.private)

    base_directory = os.path.join(blockchain.base_directory, 'blocks')

    blocks = blockchain.yield_blocks()
    expected_meta = {
        'chunk_start_block':
            0,
        'chunk_end_block':
            3,
        'chunk_file_path':
            os.path.join(
                base_directory, '0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000003-block-chunk.msgpack'
            )
    }
    for _ in range(4):
        block = next(blocks)
        block_meta = block.meta
        del block_meta['chunk_compression']  # type: ignore
        assert block_meta == expected_meta

    expected_meta = {
        'chunk_start_block':
            4,
        'chunk_end_block':
            7,
        'chunk_file_path':
            os.path.join(
                base_directory, '0/0/0/0/0/0/0/0/00000000000000000004-00000000000000000007-block-chunk.msgpack'
            )
    }
    for _ in range(4):
        block = next(blocks)
        block_meta = block.meta
        del block_meta['chunk_compression']  # type: ignore
        assert block_meta == expected_meta

    expected_meta = {
        'chunk_start_block':
            8,
        'chunk_end_block':
            None,
        'chunk_file_path':
            os.path.join(
                base_directory, '0/0/0/0/0/0/0/0/00000000000000000008-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
            )
    }
    for _ in range(2):
        block = next(blocks)
        block_meta = block.meta
        del block_meta['chunk_compression']  # type: ignore
        assert block_meta == expected_meta
