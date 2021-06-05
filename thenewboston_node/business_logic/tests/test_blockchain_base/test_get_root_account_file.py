from unittest import mock

import pytest

from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.utils.iter import get_generator

arf_1 = factories.BlockchainStateFactory(last_block_number=10)  # type: ignore
arf_2 = factories.BlockchainStateFactory(last_block_number=20)  # type: ignore


def test_can_get_account_root_file_count(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([arf_1, arf_2])):
        arf_count = blockchain_base.get_account_root_file_count()

    assert arf_count == 2


def test_can_iter_account_root_files_reversed(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([arf_1, arf_2])):
        account_root_files = list(blockchain_base.iter_account_root_files_reversed())

    assert account_root_files == [arf_2, arf_1]


def test_can_get_last_account_root_file(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([arf_1, arf_2])):
        last_arf = blockchain_base.get_last_account_root_file()

    assert last_arf == arf_2


def test_last_account_root_file_is_none(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([])):
        last_arf = blockchain_base.get_last_account_root_file()

    assert last_arf is None


def test_can_get_first_account_root_file(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([arf_1, arf_2])):
        first_arf = blockchain_base.get_first_account_root_file()

    assert first_arf == arf_1


def test_first_account_root_file_is_none(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([])):
        first_arf = blockchain_base.get_first_account_root_file()

    assert first_arf is None


def test_get_closest_blockchain_state_snapshot_validates_excludes_block_number(blockchain_base):
    with pytest.raises(ValueError):
        blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=-2)


def test_blockchain_genesis_state_not_found(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([])):
        initial_arf = blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=-1)

    assert initial_arf is None


def test_can_get_blockchain_genesis_state(blockchain_base, blockchain_genesis_state):
    arf_generator = get_generator([blockchain_genesis_state, arf_1])
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=arf_generator):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=-1)

    assert retrieved_arf == blockchain_genesis_state


@pytest.mark.parametrize('excludes_block_number', (11, 15, 20))
def test_can_exclude_last_from_closest_account_root_files(blockchain_base, excludes_block_number):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([arf_1, arf_2])):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(
            excludes_block_number=excludes_block_number
        )

    assert retrieved_arf == arf_1


def test_exclude_non_existing_account_root_file_from_closest(blockchain_base):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([arf_1, arf_2])):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(excludes_block_number=21)

    assert retrieved_arf == arf_2


@pytest.mark.parametrize('excludes_block_number', (0, 5, 10))
def test_closest_account_root_file_not_found(blockchain_base, excludes_block_number):
    with mock.patch.object(blockchain_base, 'iter_account_root_files', new=get_generator([arf_1, arf_2])):
        retrieved_arf = blockchain_base.get_closest_blockchain_state_snapshot(
            excludes_block_number=excludes_block_number
        )

    assert retrieved_arf is None
