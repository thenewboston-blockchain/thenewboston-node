import copy
import logging
from dataclasses import dataclass
from typing import Type, TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.network.base import NetworkBase
from thenewboston_node.core.utils.cryptography import normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .base import MessageMixin
from .transaction import Transaction

T = TypeVar('T', bound='TransferRequestMessage')

validation_logger = logging.getLogger(__name__ + '.validation_logger')


@fake_super_methods
@dataclass_json
@dataclass
class TransferRequestMessage(MessageMixin):
    balance_lock: str
    txs: list[Transaction]

    @classmethod
    def from_transactions(cls: Type[T], blockchain, sender: str, txs: list[Transaction]) -> T:
        return cls(
            balance_lock=blockchain.get_balance_lock(sender),
            txs=copy.deepcopy(txs),
        )

    @classmethod
    def from_main_transaction(cls: Type[T], blockchain, sender: str, recipient: str, amount: int) -> T:
        network = NetworkBase.get_instance()
        pv = network.get_primary_validator()
        node = network.get_preferred_node()
        txs = [
            Transaction(recipient=recipient, amount=amount),
            Transaction(recipient=pv.identifier, amount=pv.fee_amount, fee=True),
            Transaction(recipient=node.identifier, amount=node.fee_amount, fee=True),
        ]
        return cls.from_transactions(blockchain, sender, txs)

    def get_total_amount(self) -> int:
        return sum(tx.amount for tx in self.txs)

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['txs'] = [tx.to_dict() for tx in self.txs]
        return dict_

    def get_normalized(self) -> bytes:
        message_dict = self.to_dict()  # type: ignore

        for tx in message_dict['txs']:
            # This should fire when we add new fields to Transaction and forget to amend the sorting key
            assert len(tx) <= 3
        message_dict['txs'] = sorted(
            message_dict['txs'], key=lambda x: (x['recipient'], x.get('fee', False), x['amount'])
        )

        return normalize_dict(message_dict)

    def validate(self):
        validation_logger.debug('Validating transfer request message')
        self.validate_balance_lock()
        self.validate_transactions()
        validation_logger.debug('Transfer request message is valid')

    def validate_balance_lock(self):
        validation_logger.debug('Validating transfer request message balance lock')
        if not self.balance_lock:
            raise ValidationError('Transfer request message balance lock must be set')
        validation_logger.debug('Transfer request message balance lock is set (as expected)')
        validation_logger.debug('Transfer request message balance lock is valid')

    def validate_transactions(self):
        validation_logger.debug('Validating transfer request message transactions')

        txs = self.txs
        if not isinstance(txs, list):
            raise ValidationError('Transfer request message txs must be a list')
        validation_logger.debug('Transfer request message txs is a list (as expected)')

        if not txs:
            raise ValidationError('Transfer request message txs must contain at least one transaction')
        validation_logger.debug('Transfer request message txs contains at least one transaction (as expected)')

        for tx in self.txs:
            validation_logger.debug('Validating transaction %s on transfer request message level', tx)
            if not isinstance(tx, Transaction):
                raise ValidationError('Transfer request message txs must contain only Transactions types')
            validation_logger.debug('%s is Transaction type as expected', tx)
            tx.validate()
            validation_logger.debug('%s is valid on transfer request message level', tx)

        validation_logger.debug('Transfer request message transactions are valid')
