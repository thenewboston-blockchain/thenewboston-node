from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.utils.iter import get_generator


def test_blockchain_blockchain_genesis_state_is_validated(blockchain_base):
    initial_arf = factories.InitialAccountRootFileFactory()

    with patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf])):
        blockchain_base.validate_account_root_files(is_partial_allowed=False)


def test_blockchain_without_blockchain_genesis_state_is_validated(blockchain_base):
    non_initial_arf = factories.BlockchainStateFactory()

    with patch.object(blockchain_base, 'iter_account_root_files', get_generator([non_initial_arf])):
        blockchain_base.validate_account_root_files(is_partial_allowed=True)


def test_blockchain_must_have_at_least_blockchain_genesis_state(blockchain_base):
    with patch.object(blockchain_base, 'iter_account_root_files', get_generator([])):
        with pytest.raises(ValidationError, match='Blockchain must contain at least one account root file'):
            blockchain_base.validate_account_root_files()


def test_blockchain_must_start_with_blockchain_genesis_state(blockchain_base):
    non_initial_arf = factories.BlockchainStateFactory()

    with patch.object(blockchain_base, 'iter_account_root_files', get_generator([non_initial_arf])):
        with pytest.raises(ValidationError, match='Blockchain must start with initial account root file'):
            blockchain_base.validate_account_root_files(is_partial_allowed=False)


def test_validate_account_root_file_points_to_non_existing_block(blockchain_base):
    initial_arf = factories.InitialAccountRootFileFactory()
    block_0 = factories.CoinTransferBlockFactory(message=factories.CoinTransferBlockMessageFactory(block_number=0))
    arf_5 = factories.BlockchainStateFactory(last_block_number=5)

    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf, arf_5]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))
    with arf_patch, block_patch:
        with pytest.raises(ValidationError, match='Account root file last_block_number points to non-existing block'):
            blockchain_base.validate_account_root_files(is_partial_allowed=True)


def test_validate_account_root_file_last_block_identifier_mismatch(blockchain_base):
    next_block_identifier = '0' * 64
    block_number = 0
    initial_arf = factories.InitialAccountRootFileFactory()
    block_0 = factories.CoinTransferBlockFactory(
        message=factories.CoinTransferBlockMessageFactory(block_number=block_number, block_identifier='e' * 64),
        message_hash=next_block_identifier,
    )
    arf_0 = factories.BlockchainStateFactory(
        last_block_number=block_number,
        last_block_identifier='f' * 64,
        next_block_identifier=next_block_identifier,
    )

    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf, arf_0]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))
    with arf_patch, block_patch:
        with pytest.raises(
            ValidationError, match='Account root file last_block_number does not '
            'match last_block_identifier'
        ):
            blockchain_base.validate_account_root_files(is_partial_allowed=True)


def test_validate_account_root_file_next_block_identifier_mismatch(blockchain_base):
    last_block_identifier = '0' * 64
    block_number = 0
    initial_arf = factories.InitialAccountRootFileFactory()
    block_0 = factories.CoinTransferBlockFactory(
        message=factories.CoinTransferBlockMessageFactory(
            block_number=block_number, block_identifier=last_block_identifier
        ),
        message_hash='e' * 64,
    )
    arf_1 = factories.BlockchainStateFactory(
        last_block_number=block_number,
        last_block_identifier=last_block_identifier,
        next_block_identifier='f' * 64,
    )

    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf, arf_1]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))
    with arf_patch, block_patch:
        with pytest.raises(
            ValidationError,
            match='Account root file next_block_identifier does not match '
            'last_block_number message hash'
        ):
            blockchain_base.validate_account_root_files(is_partial_allowed=True)
