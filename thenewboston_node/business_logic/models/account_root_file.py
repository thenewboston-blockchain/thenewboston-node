from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .account_balance import AccountBalance


@dataclass_json
@dataclass
class AccountRootFile:
    accounts: dict[str, AccountBalance]
    last_block_number: Optional[int] = None
    last_block_identifier: Optional[str] = None

    def get_balance(self, account: str) -> Optional[AccountBalance]:
        return self.accounts.get(account)

    def get_balance_value(self, account: str):
        balance = self.get_balance(account)
        if balance is not None:
            return balance.balance

        return None
