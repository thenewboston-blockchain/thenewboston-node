import logging
from dataclasses import dataclass
from typing import Type, TypeVar

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode
from thenewboston_node.business_logic.validators import validate_greater_than_zero
from thenewboston_node.core.logging import timeit_method, validates
from thenewboston_node.core.utils.cryptography import derive_verify_key
from thenewboston_node.core.utils.types import hexstr

from ..signed_change_request_message import CoinTransferSignedChangeRequestMessage
from .base import SignedChangeRequest

T = TypeVar('T', bound='CoinTransferSignedChangeRequest')

logger = logging.getLogger(__name__)


@dataclass
class CoinTransferSignedChangeRequest(SignedChangeRequest):
    message: CoinTransferSignedChangeRequestMessage
    """Coin transfer request payload"""

    @classmethod
    @timeit_method(level=logging.INFO)
    def from_main_transaction(
        cls: Type[T], *, blockchain, recipient: hexstr, amount: int, signing_key: hexstr,
        primary_validator: PrimaryValidator, node: RegularNode
    ) -> T:
        message = CoinTransferSignedChangeRequestMessage.from_main_transaction(
            blockchain=blockchain,
            coin_sender=derive_verify_key(signing_key),
            recipient=recipient,
            amount=amount,
            primary_validator=primary_validator,
            node=node,
        )
        return cls.create_from_signed_change_request_message(message, signing_key)

    def get_sent_amount(self):
        assert self.message
        return self.message.get_total_amount()

    def get_recipient_amount(self, recipient):
        assert self.message
        return self.message.get_amount(recipient)

    @validates('coin transfer signed request')
    def validate(self, blockchain, in_block_number: int):
        super().validate()
        self.validate_amount(blockchain, in_block_number)
        self.validate_balance_lock(blockchain, in_block_number)

    @validates('amount on transfer request level')
    def validate_amount(self, blockchain, in_block_number: int):
        balance = blockchain.get_account_balance(self.signer, in_block_number - 1)
        validate_greater_than_zero(f'{self.humanized_class_name_lowered} singer balance', balance)

        if self.message.get_total_amount() > balance:
            raise ValidationError(f'{self.humanized_class_name} total amount is greater than signer account balance')

    @validates('transfer request balance lock on transfer request level')
    def validate_balance_lock(self, blockchain, in_block_number: int):
        if self.message.balance_lock != blockchain.get_account_balance_lock(self.signer, in_block_number - 1):
            raise ValidationError('Transfer request balance lock does not match expected balance lock')
