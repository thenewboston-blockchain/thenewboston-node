import pytest


def test_blockchain_state_is_rotated(file_blockchain_with_three_block_chunks):
    blockchain = file_blockchain_with_three_block_chunks

    assert blockchain.get_blockchain_state_count() == 3
    storage = blockchain.get_blockchain_state_storage()
    assert list(storage.list_directory()) == [
        '0000000000000000000!-blockchain-state.msgpack',
        '00000000000000000002-blockchain-state.msgpack',
        '00000000000000000005-blockchain-state.msgpack',
    ]
    assert storage.is_finalized('0000000000000000000!-blockchain-state.msgpack')
    assert storage.is_finalized('00000000000000000002-blockchain-state.msgpack')
    assert storage.is_finalized('00000000000000000005-blockchain-state.msgpack')


def test_yield_blockchain_states_is_sorted(file_blockchain_with_three_block_chunks):
    blockchain = file_blockchain_with_three_block_chunks
    assert blockchain.get_blockchain_state_count() == 3
    first, second, third = list(blockchain.yield_blockchain_states())

    assert first.is_initial()
    assert not second.is_initial()
    assert not third.is_initial()


def test_yield_blockchain_states_reversed_is_sorted_backwards(file_blockchain_with_three_block_chunks):
    first, second, third = list(file_blockchain_with_three_block_chunks.yield_blockchain_states_reversed())

    assert not first.is_initial()
    assert not second.is_initial()
    assert third.is_initial()


def test_can_get_first_blockchain_state(file_blockchain_with_three_block_chunks):
    first = file_blockchain_with_three_block_chunks.get_first_blockchain_state()
    assert first.is_initial()


def test_can_get_last_blockchain_state(file_blockchain_with_three_block_chunks):
    last = file_blockchain_with_three_block_chunks.get_last_blockchain_state()

    assert not last.is_initial()


@pytest.mark.parametrize('excludes_block_number', (-1, 0))
def test_can_get_initial_arf_with_get_closest_arf(file_blockchain_with_three_block_chunks, excludes_block_number):
    closest = file_blockchain_with_three_block_chunks.get_blockchain_state_by_block_number(excludes_block_number)
    assert closest.is_initial()


def test_closest_arf_is_last_arf(file_blockchain_with_three_block_chunks):
    closest = file_blockchain_with_three_block_chunks.get_blockchain_state_by_block_number(999)
    assert not closest.is_initial()
