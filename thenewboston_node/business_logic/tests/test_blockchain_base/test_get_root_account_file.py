import pytest

from thenewboston_node.business_logic.tests.mocks.utils import patch_blockchain_states


def test_can_get_account_root_file_count(blockchain_base, blockchain_state_10, blockchain_state_20):
    with patch_blockchain_states(blockchain_base, [blockchain_state_10, blockchain_state_20]):
        arf_count = blockchain_base.get_blockchain_states_count()

    assert arf_count == 2


def test_can_yield_blockchain_states_reversed(blockchain_base, blockchain_state_10, blockchain_state_20):
    with patch_blockchain_states(blockchain_base, [blockchain_state_10, blockchain_state_20]):
        account_root_files = list(blockchain_base.yield_blockchain_states_reversed())

    assert account_root_files == [blockchain_state_20, blockchain_state_10]


def test_can_get_last_blockchain_state(blockchain_base, blockchain_state_10, blockchain_state_20):
    with patch_blockchain_states(blockchain_base, [blockchain_state_10, blockchain_state_20]):
        last_arf = blockchain_base.get_last_blockchain_state()

    assert last_arf == blockchain_state_20


def test_last_account_root_file_is_none(blockchain_base, blockchain_state_10, blockchain_state_20):
    with patch_blockchain_states(blockchain_base, []):
        last_arf = blockchain_base.get_last_blockchain_state()

    assert last_arf is None


def test_can_get_first_blockchain_state(blockchain_base, blockchain_state_10, blockchain_state_20):
    with patch_blockchain_states(blockchain_base, [blockchain_state_10, blockchain_state_20]):
        first_arf = blockchain_base.get_first_blockchain_state()

    assert first_arf == blockchain_state_10


def test_first_account_root_file_is_none(blockchain_base):
    with patch_blockchain_states(blockchain_base, []):
        first_arf = blockchain_base.get_first_blockchain_state()

    assert first_arf is None


def test_get_closest_blockchain_state_snapshot_validates_excludes_block_number(blockchain_base):
    with pytest.raises(ValueError):
        blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=-2)


def test_blockchain_genesis_state_not_found(blockchain_base):
    with patch_blockchain_states(blockchain_base, []):
        initial_arf = blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=-1)

    assert initial_arf is None


def test_can_get_blockchain_genesis_state(blockchain_base, blockchain_genesis_state, blockchain_state_10):
    with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_10]):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=-1)

    assert retrieved_arf == blockchain_genesis_state


@pytest.mark.parametrize('excludes_block_number', (11, 15, 20))
def test_can_exclude_last_from_closest_account_root_files(
    blockchain_base, excludes_block_number, blockchain_state_10, blockchain_state_20
):
    with patch_blockchain_states(blockchain_base, [blockchain_state_10, blockchain_state_20]):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(
            excludes_block_number=excludes_block_number
        )

    assert retrieved_arf == blockchain_state_10


def test_exclude_non_existing_account_root_file_from_closest(
    blockchain_base, blockchain_state_10, blockchain_state_20
):
    with patch_blockchain_states(blockchain_base, [blockchain_state_10, blockchain_state_20]):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=21)

    assert retrieved_arf == blockchain_state_20


@pytest.mark.parametrize('excludes_block_number', (0, 5, 10))
def test_closest_account_root_file_not_found(
    blockchain_base, excludes_block_number, blockchain_state_10, blockchain_state_20
):
    with patch_blockchain_states(blockchain_base, [blockchain_state_10, blockchain_state_20]):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(
            excludes_block_number=excludes_block_number
        )

    assert retrieved_arf is None
