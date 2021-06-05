from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.utils.iter import get_generator

BLOCK_IDENTIFIER = '0' * 64
MESSAGE_HASH = '1' * 64
USER_ACCOUNT_1 = '2' * 64
USER_ACCOUNT_2 = '3' * 64

initial_arf = factories.InitialAccountRootFileFactory(
    account_states={USER_ACCOUNT_1: factories.AccountStateFactory(balance=100, balance_lock=USER_ACCOUNT_1)},
)

block_0 = factories.CoinTransferBlockFactory(
    message=factories.CoinTransferBlockMessageFactory(
        block_number=0,
        block_identifier=BLOCK_IDENTIFIER,
        signed_change_request=factories.CoinTransferSignedChangeRequestFactory(
            signer=USER_ACCOUNT_1,
            message=factories.CoinTransferSignedChangeRequestMessageFactory(
                balance_lock=USER_ACCOUNT_1,
                txs=[factories.CoinTransferTransactionFactory(
                    recipient=USER_ACCOUNT_2,
                    amount=11,
                )]
            )
        ),
        updated_account_states={
            USER_ACCOUNT_1: factories.AccountStateFactory(balance=89, balance_lock=MESSAGE_HASH),
            USER_ACCOUNT_2: factories.AccountStateFactory(balance=11, balance_lock=None),
        }
    ),
    message_hash=MESSAGE_HASH,
)


def test_validate_number_of_accounts_mismatch(blockchain_base):
    arf_0 = factories.BlockchainStateFactory(
        account_states={USER_ACCOUNT_1: factories.AccountStateFactory(balance=89, balance_lock=MESSAGE_HASH)}
    )
    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf, arf_0]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))
    with arf_patch, block_patch:
        with pytest.raises(ValidationError, match='Expected 2 accounts, but got 1 in the account root file'):
            blockchain_base.validate_account_root_files()


def test_validate_non_existent_account(blockchain_base):
    non_existent_account = 'f' * 64
    arf_0 = factories.BlockchainStateFactory(
        account_states={
            USER_ACCOUNT_1: factories.AccountStateFactory(balance=89, balance_lock=MESSAGE_HASH),
            non_existent_account: factories.AccountStateFactory(balance=11, balance_lock=non_existent_account),
        }
    )
    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf, arf_0]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))
    with arf_patch, block_patch:
        with pytest.raises(ValidationError, match=f'Could not find {USER_ACCOUNT_2} account in the account root file'):
            blockchain_base.validate_account_root_files()


def test_validate_balance_value(blockchain_base):
    wrong_balance = 0
    arf_0 = factories.BlockchainStateFactory(
        account_states={
            USER_ACCOUNT_1: factories.AccountStateFactory(balance=wrong_balance, balance_lock=MESSAGE_HASH),
            USER_ACCOUNT_2: factories.AccountStateFactory(balance=11, balance_lock=USER_ACCOUNT_2),
        }
    )
    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf, arf_0]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))
    with arf_patch, block_patch:
        with pytest.raises(
            ValidationError,
            match=f'Expected 89 balance value, but got 0 balance value for '
            f'account {USER_ACCOUNT_1}'
        ):
            blockchain_base.validate_account_root_files()


def test_validate_balance_lock(blockchain_base):
    wrong_lock = 'e' * 64
    arf_0 = factories.BlockchainStateFactory(
        account_states={
            USER_ACCOUNT_1: factories.AccountStateFactory(balance=89, balance_lock=wrong_lock),
            USER_ACCOUNT_2: factories.AccountStateFactory(balance=11, balance_lock=USER_ACCOUNT_2),
        }
    )
    arf_patch = patch.object(blockchain_base, 'iter_account_root_files', get_generator([initial_arf, arf_0]))
    block_patch = patch.object(blockchain_base, 'iter_blocks', get_generator([block_0]))
    with arf_patch, block_patch:
        with pytest.raises(
            ValidationError,
            match=f'Expected {MESSAGE_HASH} balance lock, but got {wrong_lock} '
            f'balance lock for account {USER_ACCOUNT_1}'
        ):
            blockchain_base.validate_account_root_files()
