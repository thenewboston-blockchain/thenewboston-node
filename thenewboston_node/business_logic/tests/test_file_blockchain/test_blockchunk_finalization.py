import os
import os.path
import stat
from unittest.mock import patch

import pytest
from more_itertools import ilen

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.tests.factories import add_blocks


def has_write_permissions(filename):
    return bool(os.stat(filename).st_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH))


def assert_block_chain_state_exists(file_blockchain, block_number_str):
    os.path.isfile(
        os.path.join(
            file_blockchain.get_base_directory(),
            f'blockchain-states/0/0/0/0/0/0/0/0/{block_number_str}-blockchain-state.msgpack'
        )
    )


def assert_incomplete_block_chunk_exists(file_blockchain, start_str, end_str='xxxxxxxxxxxxxxxxxxxx'):
    file_path = os.path.join(
        file_blockchain.get_base_directory(), f'block-chunks/0/0/0/0/0/0/0/0/{start_str}-{end_str}-block-chunk.msgpack'
    )
    assert os.path.isfile(file_path)
    assert has_write_permissions(file_path)


def assert_block_chunk_is_finalized(file_blockchain, start_str='00000000000000000000', end_str='00000000000000000000'):
    for compressor in ('.gz', '.xz', '.bz2', ''):
        file_path = os.path.join(
            file_blockchain.get_base_directory(),
            f'block-chunks/0/0/0/0/0/0/0/0/{start_str}-{end_str}-block-chunk.msgpack{compressor}'
        )

        if os.path.isfile(file_path) and not has_write_permissions(file_path):
            break
    else:
        pytest.fail()


@pytest.mark.order(1)
def test_can_finalize_block_chunk(file_blockchain: FileBlockchain):
    add_blocks(file_blockchain, 1)
    assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000000')
    with file_blockchain.file_lock:
        file_blockchain.finalize_block_chunk('00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack', 0)

    assert_block_chunk_is_finalized(file_blockchain, '00000000000000000000', '00000000000000000000')


@pytest.mark.order(2)
def test_block_chunk_is_finalized_on_blockchain_state_creation(file_blockchain: FileBlockchain):
    add_blocks(file_blockchain, 1)
    assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000000')
    file_blockchain.snapshot_blockchain_state()
    assert_block_chunk_is_finalized(file_blockchain)


@pytest.mark.order(3)
def test_can_add_more_blocks_after_snapshot(file_blockchain: FileBlockchain):
    assert file_blockchain.get_block_count() == 0
    add_blocks(file_blockchain, 1)
    assert file_blockchain.get_block_count() == 1
    assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000000')
    file_blockchain.snapshot_blockchain_state()
    assert_block_chunk_is_finalized(file_blockchain, '00000000000000000000', '00000000000000000000')
    add_blocks(file_blockchain, 1)
    assert file_blockchain.get_block_count() == 2
    assert_incomplete_block_chunk_exists(file_blockchain, start_str='00000000000000000001')


@pytest.mark.order(4)
def test_can_add_more_snapshots(file_blockchain: FileBlockchain):
    assert file_blockchain.get_block_count() == 0
    add_blocks(file_blockchain, 1)
    assert file_blockchain.get_block_count() == 1
    assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000000')
    file_blockchain.snapshot_blockchain_state()
    assert_block_chunk_is_finalized(file_blockchain, '00000000000000000000', '00000000000000000000')
    add_blocks(file_blockchain, 1)
    assert file_blockchain.get_block_count() == 2
    file_blockchain.snapshot_blockchain_state()
    assert_block_chunk_is_finalized(file_blockchain, '00000000000000000001', '00000000000000000001')
    assert file_blockchain.get_blockchain_state_count() == 3


@pytest.mark.order(5)
def test_automatic_snapshots(file_blockchain: FileBlockchain):
    with patch.object(file_blockchain, 'snapshot_period_in_blocks', 5):
        assert_block_chain_state_exists(file_blockchain, '0000000000000000000!')
        add_blocks(file_blockchain, 4)
        assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000000')
        add_blocks(file_blockchain, 1)
        assert_block_chain_state_exists(file_blockchain, '00000000000000000004')
        assert_block_chunk_is_finalized(file_blockchain, '00000000000000000000', '00000000000000000004')
        add_blocks(file_blockchain, 6)
        assert_block_chain_state_exists(file_blockchain, '00000000000000000009')
        assert_block_chunk_is_finalized(file_blockchain, '00000000000000000005', '00000000000000000009')
        assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000010')


@pytest.mark.order(6)
def test_blockchain_is_operational_after_blocks_added(file_blockchain: FileBlockchain):
    with patch.object(file_blockchain, 'snapshot_period_in_blocks', 5):
        add_blocks(file_blockchain, 11)
        assert_block_chain_state_exists(file_blockchain, '0000000000000000000!')
        assert_block_chain_state_exists(file_blockchain, '00000000000000000004')
        assert_block_chain_state_exists(file_blockchain, '00000000000000000009')
        assert_block_chunk_is_finalized(file_blockchain, '00000000000000000000', '00000000000000000004')
        assert_block_chunk_is_finalized(file_blockchain, '00000000000000000005', '00000000000000000009')
        assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000010')

        file_blockchain.validate(is_partial_allowed=False)
        assert ilen(file_blockchain.yield_blockchain_states()) == 3
        assert ilen(file_blockchain.yield_blocks()) == 11
        assert ilen(
            file_blockchain.yield_transactions(file_blockchain._test_treasury_account_key_pair.public)  # type: ignore
        ) > 0

        file_blockchain.clear_caches()

        file_blockchain.validate(is_partial_allowed=False)
        assert ilen(file_blockchain.yield_blockchain_states()) == 3
        assert ilen(file_blockchain.yield_blocks()) == 11
        assert ilen(
            file_blockchain.yield_transactions(file_blockchain._test_treasury_account_key_pair.public)  # type: ignore
        ) > 0

        file_blockchain.clear_caches()
        assert ilen(file_blockchain.yield_blockchain_states_reversed()) == 3
        assert ilen(file_blockchain.yield_blocks_reversed()) == 11
        assert ilen(
            file_blockchain.yield_transactions(
                file_blockchain._test_treasury_account_key_pair.public,  # type: ignore
                is_reversed=True
            )
        ) > 0


@pytest.mark.order(6)
def test_blockchain_survives_interrupted_blockchain_snapshot(file_blockchain: FileBlockchain):
    with patch.object(file_blockchain, 'snapshot_period_in_blocks', 5):
        add_blocks(file_blockchain, 7)
        with patch.object(file_blockchain, 'finalize_block_chunk'):
            add_blocks(file_blockchain, 4)
        assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000005')

        file_blockchain.validate(is_partial_allowed=False)
        assert ilen(file_blockchain.yield_blockchain_states()) == 3
        assert ilen(file_blockchain.yield_blocks()) == 11
        assert ilen(
            file_blockchain.yield_transactions(file_blockchain._test_treasury_account_key_pair.public)  # type: ignore
        ) > 0

        file_blockchain.clear_caches()
        file_blockchain.validate(is_partial_allowed=False)
        assert ilen(file_blockchain.yield_blockchain_states()) == 3
        assert ilen(file_blockchain.yield_blocks()) == 11
        assert ilen(
            file_blockchain.yield_transactions(file_blockchain._test_treasury_account_key_pair.public)  # type: ignore
        ) > 0

        file_blockchain.clear_caches()
        assert ilen(file_blockchain.yield_blockchain_states_reversed()) == 3
        assert ilen(file_blockchain.yield_blocks_reversed()) == 11
        assert ilen(
            file_blockchain.yield_transactions(
                file_blockchain._test_treasury_account_key_pair.public,  # type: ignore
                is_reversed=True
            )
        ) > 0

        add_blocks(file_blockchain, 5)

        assert_block_chain_state_exists(file_blockchain, '0000000000000000000!')
        assert_block_chain_state_exists(file_blockchain, '00000000000000000004')
        assert_block_chain_state_exists(file_blockchain, '00000000000000000009')
        assert_block_chain_state_exists(file_blockchain, '00000000000000000014')
        assert_block_chunk_is_finalized(file_blockchain, '00000000000000000000', '00000000000000000004')
        assert_block_chunk_is_finalized(file_blockchain, '00000000000000000005', '00000000000000000009')
        assert_block_chunk_is_finalized(file_blockchain, '00000000000000000010', '00000000000000000014')
        assert_incomplete_block_chunk_exists(file_blockchain, '00000000000000000015')

        file_blockchain.validate(is_partial_allowed=False)
        assert ilen(file_blockchain.yield_blockchain_states()) == 4
        assert ilen(file_blockchain.yield_blocks()) == 16
        assert ilen(
            file_blockchain.yield_transactions(file_blockchain._test_treasury_account_key_pair.public)  # type: ignore
        ) > 0

        file_blockchain.clear_caches()
        file_blockchain.validate(is_partial_allowed=False)
        assert ilen(file_blockchain.yield_blockchain_states()) == 4
        assert ilen(file_blockchain.yield_blocks()) == 16
        assert ilen(
            file_blockchain.yield_transactions(file_blockchain._test_treasury_account_key_pair.public)  # type: ignore
        ) > 0

        file_blockchain.clear_caches()
        assert ilen(file_blockchain.yield_blockchain_states_reversed()) == 4
        assert ilen(file_blockchain.yield_blocks_reversed()) == 16
        assert ilen(
            file_blockchain.yield_transactions(
                file_blockchain._test_treasury_account_key_pair.public,  # type: ignore
                is_reversed=True
            )
        ) > 0
