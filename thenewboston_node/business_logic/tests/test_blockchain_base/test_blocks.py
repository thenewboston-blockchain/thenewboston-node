from operator import attrgetter

import pytest

from thenewboston_node.business_logic.exceptions import InvalidBlockchain
from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.tests.mocks.utils import patch_blockchain_states, patch_blocks


def test_can_get_block_count(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]):
        block_count = blockchain_base.get_block_count()

    assert block_count == 3


def test_can_yield_blocks_from(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]):
        blocks = list(blockchain_base.yield_blocks_from(block_number=1))

    assert blocks == [block_1, block_2]


def test_can_yield_blocks_reversed(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]):
        blocks = list(blockchain_base.yield_blocks_reversed())

    assert blocks == [block_2, block_1, block_0]


def test_can_get_block_by_number(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]):
        block = blockchain_base.get_block_by_number(block_number=1)

    assert block == block_1


def test_get_block_by_number_returns_none_if_block_doesnt_exist(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_2]):
        block = blockchain_base.get_block_by_number(block_number=1)

    assert block is None


def test_can_get_first_block_at_init(blockchain_base):
    with patch_blocks(blockchain_base, []):
        first_block = blockchain_base.get_first_block()

    assert first_block is None


def test_can_get_first_block(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]):
        first_block = blockchain_base.get_first_block()

    assert first_block == block_0


def test_can_get_last_block_at_init(blockchain_base):
    with patch_blocks(blockchain_base, []):
        last_block = blockchain_base.get_last_block()

    assert last_block is None


def test_can_get_last_block(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]):
        last_block = blockchain_base.get_last_block()

    assert last_block == block_2


@pytest.mark.parametrize(
    'account_root_file_block_number, from_block_number, expected_block_numbers', (
        (0, 0, []),
        (0, 1, [1]),
        (0, 2, [2, 1]),
        (0, None, [2, 1]),
        (1, 0, [0]),
        (1, 1, []),
        (1, 2, [2]),
        (1, None, [2]),
        (2, 0, [0]),
        (2, 1, [1, 0]),
        (2, 2, []),
        (2, None, []),
    )
)
def test_can_yield_blocks_till_snapshot(
    blockchain_base, blockchain_genesis_state, account_root_file_block_number, from_block_number,
    expected_block_numbers, block_0, block_1, block_2
):
    blockchain_state_patch = patch_blockchain_states(
        blockchain_base, [
            blockchain_genesis_state,
            factories.BlockchainStateFactory(
                message=factories.BlockchainStateMessageFactory(last_block_number=account_root_file_block_number)
            ),
        ]
    )
    blocks_patch = patch_blocks(blockchain_base, [block_0, block_1, block_2])

    with blocks_patch, blockchain_state_patch:
        blocks = list(blockchain_base.yield_blocks_till_snapshot(from_block_number=from_block_number))

    assert list(map(attrgetter('message.block_number'), blocks)) == expected_block_numbers


def test_yield_blocks_till_snapshot_with_no_account_root_file(blockchain_base, block_0, block_1, block_2):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]), patch_blockchain_states(blockchain_base, []):
        with pytest.raises(InvalidBlockchain):
            list(blockchain_base.yield_blocks_till_snapshot())


def test_get_expected_block_identifier_validation_of_block_number(blockchain_base):
    with pytest.raises(ValueError):
        blockchain_base.get_expected_block_identifier(block_number=-1)


def test_get_expected_block_identifier_without_blockchain_genesis_state(blockchain_base):
    with patch_blockchain_states(blockchain_base, []):
        with pytest.raises(InvalidBlockchain, match='Blockchain must contain a blockchain state'):
            blockchain_base.get_expected_block_identifier(block_number=0)


def test_get_expected_block_identifier_with_blockchain_genesis_state(blockchain_base, blockchain_genesis_state):
    with patch_blockchain_states(blockchain_base, [blockchain_genesis_state]):
        block_identifier = blockchain_base.get_expected_block_identifier(block_number=0)

    assert block_identifier == blockchain_genesis_state.message.get_hash()


def test_get_expected_block_identifier_from_last_block(
    blockchain_base, blockchain_genesis_state, block_0, block_1, block_2
):
    with patch_blocks(blockchain_base, [block_0, block_1, block_2]):
        block_identifier = blockchain_base.get_expected_block_identifier(block_number=3)

    assert block_identifier == block_2.hash
