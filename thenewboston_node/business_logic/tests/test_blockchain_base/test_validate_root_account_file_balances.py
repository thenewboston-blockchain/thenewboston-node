import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.tests.mocks.utils import patch_blockchain_states, patch_blocks

BLOCK_IDENTIFIER = '0' * 64
MESSAGE_HASH = '1' * 64
USER_ACCOUNT_1 = '2' * 64
USER_ACCOUNT_2 = '3' * 64


@pytest.fixture
def blockchain_genesis_state():
    # TODO(dmu) HIGH: Remove fixtures from test_* files.
    #                 This one clashes with general blockchain_genesis_state() fixture
    return factories.InitialBlockchainStateFactory(
        account_states={USER_ACCOUNT_1: factories.AccountStateFactory(balance=100, balance_lock=USER_ACCOUNT_1)},
    )


@pytest.fixture
def block_0():
    return factories.CoinTransferBlockFactory(
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
        hash=MESSAGE_HASH,
    )


def test_validate_number_of_accounts_mismatch(blockchain_base, blockchain_genesis_state, block_0):
    arf_0 = factories.BlockchainStateFactory(
        account_states={USER_ACCOUNT_1: factories.AccountStateFactory(balance=89, balance_lock=MESSAGE_HASH)}
    )
    blockchain_state_patch = patch_blockchain_states(blockchain_base, [blockchain_genesis_state, arf_0])
    block_patch = patch_blocks(blockchain_base, [block_0])
    with blockchain_state_patch, block_patch:
        with pytest.raises(ValidationError, match='Expected 2 accounts, but got 1 in the account root file'):
            blockchain_base.validate_blockchain_states()


def test_validate_non_existent_account(blockchain_base, blockchain_genesis_state, block_0):
    non_existent_account = 'f' * 64
    state_0 = factories.BlockchainStateFactory(
        account_states={
            USER_ACCOUNT_1: factories.AccountStateFactory(balance=89, balance_lock=MESSAGE_HASH),
            non_existent_account: factories.AccountStateFactory(balance=11, balance_lock=non_existent_account),
        }
    )
    blockchain_state_patch = patch_blockchain_states(blockchain_base, [blockchain_genesis_state, state_0])
    block_patch = patch_blocks(blockchain_base, [block_0])
    with blockchain_state_patch, block_patch:
        with pytest.raises(ValidationError, match=f'Could not find {USER_ACCOUNT_2} account in the account root file'):
            blockchain_base.validate_blockchain_states()


def test_validate_balance_value(blockchain_base, blockchain_genesis_state, block_0):
    wrong_balance = 0
    state_0 = factories.BlockchainStateFactory(
        account_states={
            USER_ACCOUNT_1: factories.AccountStateFactory(balance=wrong_balance, balance_lock=MESSAGE_HASH),
            USER_ACCOUNT_2: factories.AccountStateFactory(balance=11, balance_lock=USER_ACCOUNT_2),
        }
    )
    blockchain_state_patch = patch_blockchain_states(blockchain_base, [blockchain_genesis_state, state_0])
    block_patch = patch_blocks(blockchain_base, [block_0])
    with blockchain_state_patch, block_patch:
        with pytest.raises(
            ValidationError,
            match=f'Expected 89 balance value, but got 0 balance value for '
            f'account {USER_ACCOUNT_1}'
        ):
            blockchain_base.validate_blockchain_states()


def test_validate_balance_lock(blockchain_base, blockchain_genesis_state, block_0):
    wrong_lock = 'e' * 64
    state_0 = factories.BlockchainStateFactory(
        account_states={
            USER_ACCOUNT_1: factories.AccountStateFactory(balance=89, balance_lock=wrong_lock),
            USER_ACCOUNT_2: factories.AccountStateFactory(balance=11, balance_lock=USER_ACCOUNT_2),
        }
    )
    blockchain_state_patch = patch_blockchain_states(blockchain_base, [blockchain_genesis_state, state_0])
    block_patch = patch_blocks(blockchain_base, [block_0])
    with blockchain_state_patch, block_patch:
        with pytest.raises(
            ValidationError,
            match=f'Expected {MESSAGE_HASH} balance lock, but got {wrong_lock} '
            f'balance lock for account {USER_ACCOUNT_1}'
        ):
            blockchain_base.validate_blockchain_states()
