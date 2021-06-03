import pytest

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
