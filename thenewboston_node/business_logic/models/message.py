from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .transaction import Transaction


@dataclass_json
@dataclass
class Message:
    balance_key: str
    txs: list[Transaction]

    @property
    def total_amount(self) -> int:
        return sum(tx.amount for tx in self.txs)
