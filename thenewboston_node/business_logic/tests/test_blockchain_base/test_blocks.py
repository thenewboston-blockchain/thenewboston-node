from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.utils.iter import get_generator

block_0 = factories.CoinTransferBlockFactory(message=factories.CoinTransferBlockMessageFactory(block_number=0))

block_1 = factories.CoinTransferBlockFactory(message=factories.CoinTransferBlockMessageFactory(block_number=1))

block_2 = factories.CoinTransferBlockFactory(
    message=factories.CoinTransferBlockMessageFactory(block_number=2),
    message_hash='fake-message-hash',
)


def test_can_get_block_count(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2])):
        block_count = blockchain_base.get_block_count()

    assert block_count == 3


def test_can_yield_blocks_from(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2])):
        blocks = list(blockchain_base.yield_blocks_from(block_number=1))

    assert blocks == [block_1, block_2]


def test_can_yield_blocks_reversed(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2])):
        blocks = list(blockchain_base.yield_blocks_reversed())

    assert blocks == [block_2, block_1, block_0]


def test_can_get_block_by_number(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2])):
        block = blockchain_base.get_block_by_number(block_number=1)

    assert block == block_1


def test_get_block_by_number_returns_none_if_block_doesnt_exist(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_2])):
        block = blockchain_base.get_block_by_number(block_number=1)

    assert block is None


def test_can_get_first_block_at_init(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([])):
        first_block = blockchain_base.get_first_block()

    assert first_block is None


def test_can_get_first_block(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2])):
        first_block = blockchain_base.get_first_block()

    assert first_block == block_0


def test_can_get_last_block_at_init(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([])):
        last_block = blockchain_base.get_last_block()

    assert last_block is None


def test_can_get_last_block(blockchain_base):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2])):
        last_block = blockchain_base.get_last_block()

    assert last_block == block_2


@pytest.mark.parametrize(
    'account_root_file_block_number, from_block_number, expected_blocks', (
        (0, 0, []),
        (0, 1, [block_1]),
        (0, 2, [block_2, block_1]),
        (0, None, [block_2, block_1]),
        (1, 0, [block_0]),
        (1, 1, []),
        (1, 2, [block_2]),
        (1, None, [block_2]),
        (2, 0, [block_0]),
        (2, 1, [block_1, block_0]),
        (2, 2, []),
        (2, None, []),
    )
)
def test_can_yield_blocks_till_snapshot(
    blockchain_base, blockchain_genesis_state, account_root_file_block_number, from_block_number, expected_blocks
):
    iter_arf_patch = patch.object(
        blockchain_base, 'yield_blockchain_states',
        get_generator([
            blockchain_genesis_state,
            factories.BlockchainStateFactory(last_block_number=account_root_file_block_number),
        ])
    )
    yield_blocks_patch = patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2]))

    with yield_blocks_patch, iter_arf_patch:
        blocks = list(blockchain_base.yield_blocks_till_snapshot(from_block_number=from_block_number))

    assert blocks == expected_blocks


def test_yield_blocks_till_snapshot_with_no_account_root_file(blockchain_base):
    iter_arf_patch = patch.object(blockchain_base, 'yield_blockchain_states', get_generator([]))
    yield_blocks_patch = patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2]))
    with yield_blocks_patch, iter_arf_patch:
        blocks = list(blockchain_base.yield_blocks_till_snapshot())

    assert blocks == []


def test_get_expected_block_identifier_validation_of_block_number(blockchain_base):
    with pytest.raises(ValueError):
        blockchain_base.get_expected_block_identifier(block_number=-1)


def test_get_expected_block_identifier_without_blockchain_genesis_state(blockchain_base):
    with patch.object(blockchain_base, 'yield_blockchain_states', get_generator([])):
        block_identifier = blockchain_base.get_expected_block_identifier(block_number=0)

    assert block_identifier is None


def test_get_expected_block_identifier_with_blockchain_genesis_state(blockchain_base, blockchain_genesis_state):
    with patch.object(blockchain_base, 'yield_blockchain_states', get_generator([blockchain_genesis_state])):
        block_identifier = blockchain_base.get_expected_block_identifier(block_number=0)

    assert block_identifier == blockchain_genesis_state.get_hash()


def test_get_expected_block_identifier_from_last_block(blockchain_base, blockchain_genesis_state):
    with patch.object(blockchain_base, 'yield_blocks', get_generator([block_0, block_1, block_2])):
        block_identifier = blockchain_base.get_expected_block_identifier(block_number=3)

    assert block_identifier == block_2.message_hash
