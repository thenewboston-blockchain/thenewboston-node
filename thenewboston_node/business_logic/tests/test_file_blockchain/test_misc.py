from thenewboston_node.business_logic.blockchain.file_blockchain import (
    get_block_chunk_filename_meta, get_blockchain_state_filename_meta
)


def test_get_block_chunk_filename_meta():
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack') == (12, 101, None)
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.xz') == (12, 101, 'xz')
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.bz2') == (12, 101, 'bz2')
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.gz') == (12, 101, 'gz')
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack.zip') is None
    assert get_block_chunk_filename_meta('00012-abc-block-chunk.msgpack') is None
    assert get_block_chunk_filename_meta('00012-000101-aaaaa.msgpack') is None


def test_get_blockchain_filename_meta():
    assert get_blockchain_state_filename_meta('0000012-arf.msgpack') == (12, None)
    assert get_blockchain_state_filename_meta('000000!-arf.msgpack') == (None, None)
    assert get_blockchain_state_filename_meta('0000001-arf.msgpack.xz') == (1, 'xz')
    assert get_blockchain_state_filename_meta('0000002-arf.msgpack.bz2') == (2, 'bz2')
    assert get_blockchain_state_filename_meta('0000003-arf.msgpack.gz') == (3, 'gz')
    assert get_blockchain_state_filename_meta('000aaaa-arf.msgpack') is None
    assert get_blockchain_state_filename_meta('0000012-aaa.msgpack') is None
    assert get_blockchain_state_filename_meta('0000012-arf.msgpack.zip') is None
