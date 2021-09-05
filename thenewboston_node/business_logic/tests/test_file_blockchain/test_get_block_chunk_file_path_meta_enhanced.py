import os.path

import pytest


@pytest.mark.order(1)
def test_get_block_chunk_file_path_meta_enhanced(file_blockchain_with_three_block_chunks):
    blockchain = file_blockchain_with_three_block_chunks
    meta = blockchain._get_block_chunk_file_path_meta_enhanced(
        '00000000000000000000-00000000000000000002-block-chunk.msgpack'
    )
    assert meta.filename == '00000000000000000000-00000000000000000002-block-chunk.msgpack'
    assert meta.start_block_number == 0
    assert meta.end_block_number == 2
    assert meta.compression is None
    assert meta.absolute_file_path == os.path.join(
        blockchain.get_base_directory(),
        'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz',
    )
    assert meta.blockchain_root_relative_file_path == (
        'block-chunks/0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
    )
    assert meta.storage_relative_file_path == (
        '0/0/0/0/0/0/0/0/00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
    )
