from dataclasses import dataclass
from operator import itemgetter

from dataclasses_json import dataclass_json

from thenewboston_node.core.utils.cryptography import hash_normalized_message
from thenewboston_node.core.utils.cryptography import normalize_dict_message
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .transaction import Transaction


@fake_super_methods
@dataclass_json
@dataclass
class TransferRequestMessage:
    balance_key: str
    txs: list[Transaction]

    def get_total_amount(self) -> int:
        return sum(tx.amount for tx in self.txs)

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['txs'] = [tx.to_dict() for tx in self.txs]
        return dict_

    def get_hash(self):
        return hash_normalized_message(self.get_normalized())

    def get_normalized(self) -> bytes:
        message_dict = self.to_dict()  # type: ignore
        message_dict['txs'] = sorted(message_dict['txs'], key=itemgetter('recipient'))
        return normalize_dict_message(message_dict)
