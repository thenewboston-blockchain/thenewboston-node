import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.tests.mocks.utils import patch_blockchain_states, patch_blocks


def test_blockchain_blockchain_genesis_state_is_validated(blockchain_base):
    blockchain_genesis_state = factories.InitialBlockchainStateFactory()

    with patch_blockchain_states(blockchain_base, [blockchain_genesis_state]):
        blockchain_base.validate_blockchain_states(is_partial_allowed=False)


def test_blockchain_without_blockchain_genesis_state_is_validated(blockchain_base):
    non_initial_blockchain_state = factories.BlockchainStateFactory()

    with patch_blockchain_states(blockchain_base, [non_initial_blockchain_state]):
        blockchain_base.validate_blockchain_states(is_partial_allowed=True)


def test_blockchain_must_have_at_least_blockchain_genesis_state(blockchain_base):
    with patch_blockchain_states(blockchain_base, []):
        with pytest.raises(ValidationError, match='Blockchain must contain at least one account root file'):
            blockchain_base.validate_blockchain_states()


def test_blockchain_must_start_with_blockchain_genesis_state(blockchain_base):
    non_initial_blockchain_state = factories.BlockchainStateFactory()

    with patch_blockchain_states(blockchain_base, [non_initial_blockchain_state]):
        with pytest.raises(ValidationError, match='Blockchain must start with initial account root file'):
            blockchain_base.validate_blockchain_states(is_partial_allowed=False)


def test_validate_account_root_file_points_to_non_existing_block(blockchain_base):
    blockchain_genesis_state = factories.InitialBlockchainStateFactory()
    block_0 = factories.CoinTransferBlockFactory(message=factories.CoinTransferBlockMessageFactory(block_number=0))
    state_5 = factories.BlockchainStateFactory(last_block_number=5)

    blockchain_state_patch = patch_blockchain_states(blockchain_base, [blockchain_genesis_state, state_5])
    block_patch = patch_blocks(blockchain_base, [block_0])
    with blockchain_state_patch, block_patch:
        with pytest.raises(ValidationError, match='Account root file last_block_number points to non-existing block'):
            blockchain_base.validate_blockchain_states(is_partial_allowed=True)


def test_validate_account_root_file_last_block_identifier_mismatch(blockchain_base):
    next_block_identifier = '0' * 64
    block_number = 0
    blockchain_genesis_state = factories.InitialBlockchainStateFactory()
    block_0 = factories.CoinTransferBlockFactory(
        message=factories.CoinTransferBlockMessageFactory(block_number=block_number, block_identifier='e' * 64),
        hash=next_block_identifier,
    )
    state_0 = factories.BlockchainStateFactory(
        last_block_number=block_number,
        last_block_identifier='f' * 64,
        next_block_identifier=next_block_identifier,
    )

    blockchain_state_patch = patch_blockchain_states(blockchain_base, [blockchain_genesis_state, state_0])
    block_patch = patch_blocks(blockchain_base, [block_0])
    with blockchain_state_patch, block_patch:
        with pytest.raises(
            ValidationError, match='Account root file last_block_number does not '
            'match last_block_identifier'
        ):
            blockchain_base.validate_blockchain_states(is_partial_allowed=True)


def test_validate_account_root_file_next_block_identifier_mismatch(blockchain_base):
    last_block_identifier = '0' * 64
    block_number = 0
    blockchain_genesis_state = factories.InitialBlockchainStateFactory()
    block_0 = factories.CoinTransferBlockFactory(
        message=factories.CoinTransferBlockMessageFactory(
            block_number=block_number, block_identifier=last_block_identifier
        ),
        hash='e' * 64,
    )
    state_1 = factories.BlockchainStateFactory(
        last_block_number=block_number,
        last_block_identifier=last_block_identifier,
        next_block_identifier='f' * 64,
    )

    blockchain_state_patch = patch_blockchain_states(blockchain_base, [blockchain_genesis_state, state_1])
    block_patch = patch_blocks(blockchain_base, [block_0])
    with blockchain_state_patch, block_patch:
        with pytest.raises(
            ValidationError,
            match='Account root file next_block_identifier does not match '
            'last_block_number message hash'
        ):
            blockchain_base.validate_blockchain_states(is_partial_allowed=True)
