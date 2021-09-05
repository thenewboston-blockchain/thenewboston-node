import pytest


def get_block_numbers(blocks):
    return list(map(lambda b: b.message.block_number, blocks))


def test_can_yield_blocks(file_blockchain_with_three_block_chunks):
    blocks = file_blockchain_with_three_block_chunks.yield_blocks()
    assert get_block_numbers(blocks) == [0, 1, 2, 3, 4, 5, 6, 7]


def test_can_yield_blocks_reversed(file_blockchain_with_three_block_chunks):
    blocks = file_blockchain_with_three_block_chunks.yield_blocks_reversed()
    assert get_block_numbers(blocks) == [7, 6, 5, 4, 3, 2, 1, 0]


def test_yield_blocks_from_file_cache(file_blockchain_with_three_block_chunks):
    blocks = file_blockchain_with_three_block_chunks._yield_blocks_from_file_cached(
        '00000000000000000000-00000000000000000002-block-chunk.msgpack', -1, start=0
    )
    assert get_block_numbers(blocks) == [0]


@pytest.mark.parametrize(
    'block_number, expected_block_numbers', (
        (0, [0, 1, 2, 3, 4, 5, 6, 7]),
        (1, [1, 2, 3, 4, 5, 6, 7]),
        (2, [2, 3, 4, 5, 6, 7]),
        (3, [3, 4, 5, 6, 7]),
        (7, [7]),
    )
)
def test_can_yield_blocks_from(file_blockchain_with_three_block_chunks, block_number, expected_block_numbers):
    blocks = file_blockchain_with_three_block_chunks.yield_blocks_from(block_number=block_number)
    assert get_block_numbers(blocks) == expected_block_numbers


def test_can_get_block_count(file_blockchain_with_three_block_chunks):
    assert file_blockchain_with_three_block_chunks.get_block_count() == 8


def test_can_get_block_by_number(file_blockchain_with_three_block_chunks):
    received_block = file_blockchain_with_three_block_chunks.get_block_by_number(block_number=1)
    assert received_block.message.block_number == 1
    assert received_block.get_block_number() == 1


def test_get_block_by_number_returns_none_if_not_exist(file_blockchain_with_three_block_chunks):
    received_block = file_blockchain_with_three_block_chunks.get_block_by_number(block_number=999)
    assert received_block is None


def test_can_get_first_block(file_blockchain_with_three_block_chunks):
    block = file_blockchain_with_three_block_chunks.get_first_block()
    assert block.message.block_number == 0


def test_can_get_last_block(file_blockchain_with_three_block_chunks):
    block = file_blockchain_with_three_block_chunks.get_last_block()
    assert block.message.block_number == 7


def test_can_yield_blocks_till_snapshot(file_blockchain_with_three_block_chunks):
    blocks = list(file_blockchain_with_three_block_chunks.yield_blocks_till_snapshot())
    assert get_block_numbers(blocks) == [7, 6]


def test_can_yield_blocks_till_snapshot_from_block_number(file_blockchain_with_three_block_chunks):
    blocks = file_blockchain_with_three_block_chunks.yield_blocks_till_snapshot(from_block_number=4)

    assert get_block_numbers(blocks) == [4, 3]
