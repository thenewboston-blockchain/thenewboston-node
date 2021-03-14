import copy
from dataclasses import dataclass
from operator import itemgetter
from typing import Type, TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.network.base import NetworkBase
from thenewboston_node.core.utils.cryptography import normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .base import MessageMixin
from .transaction import Transaction

T = TypeVar('T', bound='TransferRequestMessage')


@fake_super_methods
@dataclass_json
@dataclass
class TransferRequestMessage(MessageMixin):
    balance_lock: str
    txs: list[Transaction]

    @classmethod
    def from_transactions(cls: Type[T], sender: str, txs: list[Transaction]) -> T:
        from thenewboston_node.business_logic.blockchain.base import BlockchainBase
        return cls(
            balance_lock=BlockchainBase.get_instance().get_account_balance_lock(sender),
            txs=copy.deepcopy(txs),
        )

    @classmethod
    def from_main_transaction(cls: Type[T], sender: str, recipient: str, amount: int) -> T:
        network = NetworkBase.get_instance()
        pv = network.get_primary_validator()
        node = network.get_preferred_node()
        txs = [
            Transaction(recipient=recipient, amount=amount),
            Transaction(recipient=pv.identifier, amount=pv.fee_amount, fee=pv.type_),
            Transaction(recipient=node.identifier, amount=node.fee_amount, fee=node.type_),
        ]
        return cls.from_transactions(sender, txs)

    def get_total_amount(self) -> int:
        return sum(tx.amount for tx in self.txs)

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['txs'] = [tx.to_dict() for tx in self.txs]
        return dict_

    def get_normalized(self) -> bytes:
        message_dict = self.to_dict()  # type: ignore
        message_dict['txs'] = sorted(message_dict['txs'], key=itemgetter('recipient'))
        return normalize_dict(message_dict)
