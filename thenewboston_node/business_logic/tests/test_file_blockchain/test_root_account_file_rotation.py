from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key


@pytest.fixture(autouse=True)
def set_up(file_blockchain_w_memory_storage, user_account, treasury_account_signing_key, preferred_node):
    signing_key = treasury_account_signing_key
    with patch.object(file_blockchain_w_memory_storage, 'snapshot_period_in_blocks', 2):
        block0 = Block.create_from_main_transaction(
            blockchain=file_blockchain_w_memory_storage,
            recipient=user_account,
            amount=10,
            request_signing_key=signing_key,
            pv_signing_key=get_node_signing_key(),
            preferred_node=preferred_node,
        )
        file_blockchain_w_memory_storage.add_block(block0)

        block1 = Block.create_from_main_transaction(
            blockchain=file_blockchain_w_memory_storage,
            recipient=user_account,
            amount=20,
            request_signing_key=signing_key,
            pv_signing_key=get_node_signing_key(),
            preferred_node=preferred_node,
        )
        file_blockchain_w_memory_storage.add_block(block1)


def test_account_root_file_is_rotated(file_blockchain_w_memory_storage):
    blockchain = file_blockchain_w_memory_storage
    initial_arf_filename = '000000000!-blockchain-state.msgpack'
    new_blockchain_state = '0000000001-blockchain-state.msgpack'

    assert blockchain.get_blockchain_states_count() == 2
    assert blockchain.blockchain_states_storage.files.keys() == {initial_arf_filename, new_blockchain_state}
    assert blockchain.blockchain_states_storage.finalized == {initial_arf_filename, new_blockchain_state}


def test_yield_blockchain_states_is_sorted(file_blockchain_w_memory_storage):
    blockchain = file_blockchain_w_memory_storage
    first_arf, second_arf = list(blockchain.yield_blockchain_states())

    assert first_arf.is_initial()
    assert not second_arf.is_initial()


def test_yield_blockchain_states_reversed_is_sorted_backwards(file_blockchain_w_memory_storage):
    first_arf, second_arf = list(file_blockchain_w_memory_storage.yield_blockchain_states_reversed())

    assert not first_arf.is_initial()
    assert second_arf.is_initial()


def test_can_get_first_blockchain_state(file_blockchain_w_memory_storage):
    first_arf = file_blockchain_w_memory_storage.get_first_blockchain_state()

    assert first_arf.is_initial()


def test_can_get_last_blockchain_state(file_blockchain_w_memory_storage):
    last_arf = file_blockchain_w_memory_storage.get_last_blockchain_state()

    assert not last_arf.is_initial()


@pytest.mark.parametrize('excludes_block_number', (-1, 0))
def test_can_get_initial_arf_with_get_closest_arf(file_blockchain_w_memory_storage, excludes_block_number):
    closest_arf = file_blockchain_w_memory_storage.get_blockchain_state_by_block_number(excludes_block_number)

    assert closest_arf.is_initial()


def test_closest_arf_is_last_arf(file_blockchain_w_memory_storage):
    closest_arf = file_blockchain_w_memory_storage.get_blockchain_state_by_block_number(999)

    assert not closest_arf.is_initial()
