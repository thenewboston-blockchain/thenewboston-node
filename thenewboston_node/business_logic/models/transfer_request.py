import copy
import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.cryptography import derive_verify_key
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .base import SignableMixin
from .transfer_request_message import TransferRequestMessage

T = TypeVar('T', bound='TransferRequest')

logger = logging.getLogger(__name__)
validation_logger = logging.getLogger(__name__ + '.validation_logger')


@fake_super_methods
@dataclass_json
@dataclass
class TransferRequest(SignableMixin):
    verify_key_field_name = 'sender'

    sender: str
    message: TransferRequestMessage
    message_signature: Optional[str] = None

    @classmethod
    def from_transfer_request_message(cls: Type[T], message: TransferRequestMessage, signing_key: str) -> T:
        request = cls(sender=derive_verify_key(signing_key), message=copy.deepcopy(message))
        request.sign(signing_key)
        return request

    @classmethod
    def from_main_transaction(cls: Type[T], blockchain, recipient: str, amount: int, signing_key: str) -> T:
        sender = derive_verify_key(signing_key)
        message = TransferRequestMessage.from_main_transaction(blockchain, sender, recipient, amount)
        return cls.from_transfer_request_message(message, signing_key)

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['message'] = self.message.to_dict()
        return dict_

    def validate(self, blockchain, block_number: Optional[int] = None):
        validation_logger.debug('Validating transfer request')
        self.validate_sender()
        self.validate_message()
        self.validate_signature()
        self.validate_amount(blockchain, block_number)
        self.validate_balance_lock(blockchain, block_number)
        validation_logger.debug('Transfer request is valid')

    def validate_sender(self):
        validation_logger.debug('Validating transfer request sender')
        if not self.sender:
            raise ValidationError('Transfer request sender must be set')
        validation_logger.debug('Transfer request sender is set (as expected)')

        if not isinstance(self.sender, str):
            raise ValidationError('Transfer request sender must be a string')
        validation_logger.debug('Transfer request sender is a string')
        validation_logger.debug('Transfer request sender is valid')

    def validate_message(self):
        self.message.validate()

    def validate_amount(self, blockchain, on_block_number: Optional[int] = None):
        validation_logger.debug('Validating amount on transfer request level')
        balance = blockchain.get_balance_value(self.sender, on_block_number)
        if balance is None:
            raise ValidationError('Transfer request sender account balance is not found')
        validation_logger.debug('Transfer request sender has balance (as expected)')

        if self.message.get_total_amount() > balance:
            raise ValidationError('Transfer request transactions total amount is greater than sender account balance')
        validation_logger.debug('Transfer request sender has enough funds to transfer')
        validation_logger.debug('Amount is valid on transfer request level')

    def validate_balance_lock(self, blockchain, block_number: Optional[int] = None):
        validation_logger.debug('Validating transfer request balance lock on transfer request level')
        if self.message.balance_lock != blockchain.get_balance_lock(self.sender, block_number):
            raise ValidationError('Transfer request balance lock does not match expected balance lock')
        validation_logger.debug('Transfer request balance lock matches expected balance lock')
        validation_logger.debug('Transfer request balance lock is valid on transfer request level')
