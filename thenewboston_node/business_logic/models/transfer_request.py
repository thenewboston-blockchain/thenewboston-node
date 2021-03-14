import copy
import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from dataclasses_json import dataclass_json

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

    message: TransferRequestMessage
    sender: Optional[str] = None
    message_signature: Optional[str] = None

    def __post_init__(self):
        self.validation_errors: list[str] = []

    @classmethod
    def from_transfer_request_message(cls: Type[T], message: TransferRequestMessage, signing_key: str) -> T:
        request = cls(message=copy.deepcopy(message))
        request.sign(signing_key)
        return request

    @classmethod
    def from_main_transaction(cls: Type[T], sender: str, recipient: str, amount: int, *, signing_key: str) -> T:
        message = TransferRequestMessage.from_main_transaction(sender, recipient, amount)
        return cls.from_transfer_request_message(message, signing_key)

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['message'] = self.message.to_dict()
        return dict_

    def add_validation_error(self, error_message: str):
        self.validation_errors.append(error_message)

    def is_valid(self) -> bool:
        if self.validation_errors:
            self.validation_errors = []

        return self.is_signature_valid() and self.is_amount_valid() and self.is_balance_lock_valid()

    def is_signature_valid(self) -> bool:
        if not super().is_signature_valid():
            self.add_validation_error('Message signature is invalid')
            return False

        return True

    def is_amount_valid(self) -> bool:
        balance = get_blockchain().get_account_balance(self.sender)
        if balance is None:
            self.add_validation_error('Account balance is not found')
            return False

        if self.message.get_total_amount() > balance:
            self.add_validation_error('Transaction total amount is greater than account balance')
            return False

        return True

    def is_balance_lock_valid(self) -> bool:
        if self.message.balance_lock != get_blockchain().get_account_balance_lock(self.sender):
            self.add_validation_error('Balance key does not match balance lock')
            return False

        return True
