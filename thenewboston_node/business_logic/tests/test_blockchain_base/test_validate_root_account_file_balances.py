import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests.baker_factories import make_account_state
from thenewboston_node.business_logic.tests.mocks.utils import patch_blockchain_states, patch_blocks
from thenewboston_node.core.utils.types import hexstr

NON_EXISTENT_ACCOUNT = hexstr('f' * 64)


def test_validate_number_of_accounts_mismatch(blockchain_base, blockchain_genesis_state, block_0):
    with patch_blocks(blockchain_base, [block_0]):
        blockchain_state_0 = blockchain_base.generate_blockchain_state()
        blockchain_state_0.account_states |= {NON_EXISTENT_ACCOUNT: make_account_state()}

        with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_0]):
            with pytest.raises(ValidationError, match='Expected 4 accounts, but got 5 in the blockchain state'):
                blockchain_base.validate_blockchain_states()


def test_validate_non_existent_account(blockchain_base, blockchain_genesis_state, block_0, treasury_account):
    with patch_blocks(blockchain_base, [block_0]):
        blockchain_state_0 = blockchain_base.generate_blockchain_state()
        treasury_account_state = blockchain_state_0.account_states.pop(treasury_account)
        blockchain_state_0.account_states[NON_EXISTENT_ACCOUNT] = treasury_account_state

        with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_0]):
            with pytest.raises(
                ValidationError, match=f'Could not find {treasury_account} account in the blockchain state'
            ):
                blockchain_base.validate_blockchain_states()


def test_validate_balance_value(blockchain_base, blockchain_genesis_state, block_0, user_account):
    with patch_blocks(blockchain_base, [block_0]):
        blockchain_state_0 = blockchain_base.generate_blockchain_state()
        blockchain_state_0.account_states[user_account].balance = 999

        with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_0]):
            with pytest.raises(
                ValidationError,
                match=f'Expected 99 balance value, but got 999 balance value for account {user_account}'
            ):
                blockchain_base.validate_blockchain_states()


def test_validate_balance_lock(blockchain_base, blockchain_genesis_state, block_0, user_account):
    with patch_blocks(blockchain_base, [block_0]):
        blockchain_state_0 = blockchain_base.generate_blockchain_state()
        orig_balance_lock = blockchain_state_0.account_states[user_account].balance_lock
        blockchain_state_0.account_states[user_account].balance_lock = 'wrong-lock'

        with patch_blockchain_states(blockchain_base, [blockchain_genesis_state, blockchain_state_0]):
            with pytest.raises(
                ValidationError,
                match=f'Expected {orig_balance_lock} balance lock, but got wrong-lock balance lock for '
                f'account {user_account}'
            ):
                blockchain_base.validate_blockchain_states()
