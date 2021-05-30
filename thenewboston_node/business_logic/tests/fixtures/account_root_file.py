import pytest

from thenewboston_node.business_logic.models.account_root_file import BlockchainState
from thenewboston_node.business_logic.models.account_state import AccountState


@pytest.fixture
def treasury_initial_balance():
    return 281474976710656


@pytest.fixture
def initial_account_root_file(treasury_account, treasury_initial_balance) -> BlockchainState:
    accounts = {treasury_account: AccountState(balance=treasury_initial_balance, balance_lock=treasury_account)}
    return BlockchainState(account_states=accounts)


@pytest.fixture
def initial_account_root_file_dict(initial_account_root_file: BlockchainState) -> dict:
    return initial_account_root_file.to_dict()  # type: ignore
