import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests.baker_factories import make_blockchain_state, make_genesis_blockchain_state
from thenewboston_node.business_logic.tests.mocks.utils import patch_blockchain_states, patch_blocks


def test_blockchain_blockchain_genesis_state_is_validated(blockchain_base):
    blockchain_genesis_state = make_genesis_blockchain_state()

    with patch_blockchain_states(blockchain_base, [blockchain_genesis_state]):
        blockchain_base.validate_blockchain_states(is_partial_allowed=False)


def test_blockchain_without_blockchain_genesis_state_is_validated(blockchain_base):
    non_initial_blockchain_state = make_blockchain_state()

    with patch_blockchain_states(blockchain_base, [non_initial_blockchain_state]):
        blockchain_base.validate_blockchain_states(is_partial_allowed=True)


def test_blockchain_must_have_at_least_blockchain_genesis_state(blockchain_base):
    with patch_blockchain_states(blockchain_base, []):
        with pytest.raises(ValidationError, match='Blockchain must contain at least one blockchain state'):
            blockchain_base.validate_blockchain_states()


def test_blockchain_must_start_with_blockchain_genesis_state(blockchain_base):
    non_initial_blockchain_state = make_blockchain_state()

    with patch_blockchain_states(blockchain_base, [non_initial_blockchain_state]):
        with pytest.raises(ValidationError, match='Blockchain must start with initial blockchain state'):
            blockchain_base.validate_blockchain_states(is_partial_allowed=False)


def test_validate_blockchain_state_points_to_non_existing_block(blockchain_base, blockchain_genesis_state, block_0):
    with patch_blocks(blockchain_base, [block_0]):
        blockchain_state_5 = blockchain_base.generate_blockchain_state()
        blockchain_state_5.last_block_number = 5

        with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_5]):
            with pytest.raises(
                ValidationError, match='Blockchain state last_block_number points to non-existing block'
            ):
                blockchain_base.validate_blockchain_states(is_partial_allowed=True)


def test_validate_blockchain_state_last_block_identifier_mismatch(blockchain_base, blockchain_genesis_state, block_0):
    with patch_blocks(blockchain_base, [block_0]):
        blockchain_state_0 = blockchain_base.generate_blockchain_state()
        blockchain_state_0.last_block_identifier = 'wrong-identifier'

        with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_0]):
            with pytest.raises(
                ValidationError, match='Blockchain state last_block_identifier does not match block_identifier'
            ):
                blockchain_base.validate_blockchain_states(is_partial_allowed=True)


def test_validate_blockchain_state_next_block_identifier_mismatch(blockchain_base, blockchain_genesis_state, block_0):
    with patch_blocks(blockchain_base, [block_0]):
        blockchain_state_0 = blockchain_base.generate_blockchain_state()
        blockchain_state_0.next_block_identifier = 'wrong-identifier'

        with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_0]):
            with pytest.raises(
                ValidationError,
                match='Blockchain state next_block_identifier does not match last_block_number message hash'
            ):
                blockchain_base.validate_blockchain_states(is_partial_allowed=True)
