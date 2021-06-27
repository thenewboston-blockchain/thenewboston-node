import pytest

from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState


@pytest.fixture
def treasury_initial_balance():
    return 281474976710656


@pytest.fixture
def blockchain_genesis_state(treasury_account, treasury_initial_balance) -> BlockchainState:
    accounts = {treasury_account: AccountState(balance=treasury_initial_balance, balance_lock=treasury_account)}
    return BlockchainState(account_states=accounts)


@pytest.fixture
def blockchain_genesis_state_dict(blockchain_genesis_state: BlockchainState) -> dict:
    return blockchain_genesis_state.to_dict()  # type: ignore


@pytest.fixture
def blockchain_state_10(treasury_initial_balance, treasury_account, user_account):
    user_balance = 1000
    return models.BlockchainState(
        last_block_number=10,
        account_states={
            treasury_account:
                AccountState(balance=treasury_initial_balance - user_balance, balance_lock=treasury_account),
            user_account:
                AccountState(balance=user_balance, balance_lock=user_account),
        },
    )


@pytest.fixture
def blockchain_state_20(treasury_initial_balance, treasury_account, user_account):
    user_balance = 2000
    return models.BlockchainState(
        last_block_number=20,
        account_states={
            treasury_account:
                AccountState(balance=treasury_initial_balance - user_balance, balance_lock=treasury_account),
            user_account:
                AccountState(balance=user_balance, balance_lock=user_account),
        },
    )
