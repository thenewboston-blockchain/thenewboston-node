from thenewboston_node.business_logic.blockchain.file_blockchain import (
    get_block_chunk_filename_meta, get_blockchain_state_filename_meta
)


def test_get_block_chunk_filename_meta():
    assert get_block_chunk_filename_meta('00012-000101-block-chunk.msgpack') == (12, 101)
    assert get_block_chunk_filename_meta('00012-abc-block-chunk.msgpack') is None
    assert get_block_chunk_filename_meta('00012-000101-aaaaa.msgpack') is None


def test_get_blockchain_filename_meta():
    assert get_blockchain_state_filename_meta('0000012-arf.msgpack') == (12,)
    assert get_blockchain_state_filename_meta('000000!-arf.msgpack') == (None,)
    assert get_blockchain_state_filename_meta('000aaaa-arf.msgpack') is None
    assert get_blockchain_state_filename_meta('0000012-aaa.msgpack') is None
