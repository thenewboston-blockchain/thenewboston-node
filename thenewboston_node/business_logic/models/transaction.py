from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Transaction:
    amount: int
    recipient: str
    fee: Optional[str] = None
