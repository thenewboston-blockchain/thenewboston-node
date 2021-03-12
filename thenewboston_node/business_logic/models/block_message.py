from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .account_balance import AccountBalance
from .transfer_request import TransferRequest


@dataclass_json
@dataclass
class BlockMessage:
    transfer_request: TransferRequest
    block_identifier: str
    updated_balances: list[AccountBalance]
