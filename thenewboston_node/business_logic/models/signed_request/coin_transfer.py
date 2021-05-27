import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode
from thenewboston_node.core.logging import timeit_method, validates
from thenewboston_node.core.utils.cryptography import derive_verify_key
from thenewboston_node.core.utils.dataclass import fake_super_methods

from ..signed_request_message import CoinTransferSignedRequestMessage
from .base import SignedRequest

T = TypeVar('T', bound='CoinTransferSignedRequest')

logger = logging.getLogger(__name__)


@fake_super_methods
@dataclass_json
@dataclass
class CoinTransferSignedRequest(SignedRequest):
    message: CoinTransferSignedRequestMessage
    """Transfer request payload"""

    @classmethod
    @timeit_method(level=logging.INFO)
    def from_main_transaction(
        cls: Type[T], *, blockchain, recipient: str, amount: int, signing_key: str,
        primary_validator: PrimaryValidator, node: RegularNode
    ) -> T:
        message = CoinTransferSignedRequestMessage.from_main_transaction(
            blockchain=blockchain,
            coin_sender=derive_verify_key(signing_key),
            recipient=recipient,
            amount=amount,
            primary_validator=primary_validator,
            node=node,
        )
        return cls.from_signed_request_message(message, signing_key)

    def override_to_dict(self):
        # we can and should call base method the normal way because it is defined in the base class
        return super().to_dict()

    def get_sent_amount(self):
        assert self.message
        return self.message.get_total_amount()

    def get_recipient_amount(self, recipient):
        assert self.message
        return self.message.get_amount(recipient)

    @validates('coin transfer signed request')
    def validate(self, blockchain, block_number: Optional[int] = None):
        super().validate()
        self.validate_amount(blockchain, block_number)
        self.validate_balance_lock(blockchain, block_number)

    @validates('amount on transfer request level')
    def validate_amount(self, blockchain, on_block_number: Optional[int] = None):
        balance = blockchain.get_balance_value(self.signer, on_block_number)
        if balance is None:
            raise ValidationError('Transfer request signer account balance is not found')

        if self.message.get_total_amount() > balance:
            raise ValidationError('Transfer request transactions total amount is greater than signer account balance')

    @validates('transfer request balance lock on transfer request level')
    def validate_balance_lock(self, blockchain, block_number: Optional[int] = None):
        if self.message.balance_lock != blockchain.get_balance_lock(self.signer, block_number):
            raise ValidationError('Transfer request balance lock does not match expected balance lock')
