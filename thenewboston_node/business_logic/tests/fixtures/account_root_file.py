import pytest

from thenewboston_node.business_logic.models.account_balance import AccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile


@pytest.fixture
def treasury_initial_balance():
    return 281474976710656


@pytest.fixture
def initial_account_root_file(treasury_account, treasury_initial_balance) -> AccountRootFile:
    accounts = {treasury_account: AccountBalance(value=treasury_initial_balance, lock=treasury_account)}
    return AccountRootFile(accounts=accounts)


@pytest.fixture
def initial_account_root_file_dict(initial_account_root_file: AccountRootFile) -> dict:
    return initial_account_root_file.to_dict()  # type: ignore
