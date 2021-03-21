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


def get_blockchain():
    # TODO(dmu) LOW: Find a better way to avoid circular imports
    from ..blockchain.base import BlockchainBase  # noqa: E402,I202
    return BlockchainBase.get_instance()


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
    def from_main_transaction(cls: Type[T], recipient: str, amount: int, signing_key: str) -> T:
        sender = derive_verify_key(signing_key)
        message = TransferRequestMessage.from_main_transaction(sender, recipient, amount)
        return cls.from_transfer_request_message(message, signing_key)

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['message'] = self.message.to_dict()
        return dict_

    def validate(self):
        self.validate_sender()
        self.validate_message()
        self.validate_signature()
        self.validate_amount()
        self.validate_balance_lock()

    def validate_sender(self):
        if not self.sender:
            raise ValidationError('Transfer request sender must be set')

        if not isinstance(self.sender, str):
            raise ValidationError('Transfer request sender must be an account number string')

    def validate_message(self):
        self.message.validate()

    def validate_amount(self):
        balance = get_blockchain().get_account_balance(self.sender)
        if balance is None:
            raise ValidationError('Account balance is not found')

        if self.message.get_total_amount() > balance:
            raise ValidationError('Transaction total amount is greater than account balance')

    def validate_balance_lock(self):
        if self.message.balance_lock != get_blockchain().get_account_balance_lock(self.sender):
            raise ValidationError('Balance key does not match balance lock')
