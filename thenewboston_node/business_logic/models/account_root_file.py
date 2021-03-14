from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


# TODO(dmu) MEDIUM: Consider merge with `thenewboston_node.business_logic.models.account_balance.AccountBalance`
@dataclass_json
@dataclass
class AccountRootFileAccountBalance:
    balance: int
    balance_lock: str


@dataclass_json
@dataclass
class AccountRootFile:
    accounts: dict[str, AccountRootFileAccountBalance]
    last_block_number: Optional[int] = None
