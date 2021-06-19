import copy
from dataclasses import dataclass
from typing import Type, TypeVar

from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode
from thenewboston_node.business_logic.validators import validate_not_empty, validate_type
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import normalize_dict
from thenewboston_node.core.utils.types import hexstr

from .base import SignedChangeRequestMessage
from .coin_transfer_transaction import CoinTransferTransaction

T = TypeVar('T', bound='CoinTransferSignedChangeRequestMessage')


@dataclass
class CoinTransferSignedChangeRequestMessage(SignedChangeRequestMessage):
    """Coin transfer request message"""

    balance_lock: hexstr
    """Sender balance lock"""

    txs: list[CoinTransferTransaction]
    """List of transactions: `CoinTransferTransaction`_"""

    @classmethod
    def from_transactions(cls: Type[T], blockchain, coin_sender: str, txs: list[CoinTransferTransaction]) -> T:
        return cls(
            balance_lock=blockchain.get_account_current_balance_lock(coin_sender),
            txs=copy.deepcopy(txs),
        )

    @classmethod
    def from_main_transaction(
        cls: Type[T], *, blockchain, coin_sender: hexstr, recipient: hexstr, amount: int,
        primary_validator: PrimaryValidator, node: RegularNode
    ) -> T:
        txs = [
            CoinTransferTransaction(recipient=recipient, amount=amount),
            CoinTransferTransaction(
                recipient=primary_validator.fee_account or primary_validator.identifier,
                amount=primary_validator.fee_amount,
                fee=True
            ),
            CoinTransferTransaction(recipient=node.fee_account or node.identifier, amount=node.fee_amount, fee=True),
        ]
        return cls.from_transactions(blockchain, coin_sender, txs)

    def get_total_amount(self) -> int:
        return sum(tx.amount for tx in self.txs)

    def get_amount(self, recipient):
        return sum(tx.amount for tx in self.txs if tx.recipient == recipient)

    def get_normalized(self) -> bytes:
        message_dict = self.serialize_to_dict()  # type: ignore

        for tx in message_dict['txs']:
            # This should fire when we add new fields to CoinTransferTransaction and forget to amend the sorting key
            assert len(tx) <= 3
        message_dict['txs'] = sorted(
            message_dict['txs'], key=lambda x: (x['recipient'], x.get('fee', False), x['amount'])
        )

        return normalize_dict(message_dict)

    @validates('transfer request message')
    def validate(self):
        self.validate_balance_lock()
        self.validate_transactions()

    @validates('transfer request message balance lock')
    def validate_balance_lock(self):
        validate_not_empty(f'{self.humanized_class_name} balance lock', self.balance_lock)

    @validates('transfer request message transactions', is_plural_target=True)
    def validate_transactions(self):
        txs = self.txs
        validate_type(f'{self.humanized_class_name} txs', txs, list)
        validate_not_empty(f'{self.humanized_class_name} txs', txs)

        for tx in self.txs:
            with validates(f'Validating transaction {tx} on {self.get_humanized_class_name(False)} level'):
                validate_type(f'{self.humanized_class_name} txs', tx, CoinTransferTransaction)
                tx.validate()
