from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class AccountBalance:
    account_number: str
    balance: int
    balance_lock: Optional[str] = None
