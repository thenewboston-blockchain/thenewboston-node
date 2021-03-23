import pytest

from thenewboston_node.business_logic.models.account_balance import AccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile


@pytest.fixture
def initial_account_root_file(treasury_account_key_pair) -> AccountRootFile:
    account = treasury_account_key_pair.public
    return AccountRootFile(accounts={account: AccountBalance(value=281474976710656, lock=account)})


@pytest.fixture
def initial_account_root_file_dict(initial_account_root_file: AccountRootFile) -> dict:
    return initial_account_root_file.to_dict()  # type: ignore
