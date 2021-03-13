from dataclasses import dataclass

from dataclasses_json import dataclass_json

from thenewboston_node.core.utils.cryptography import is_valid_signature
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .transfer_request_message import TransferRequestMessage


@fake_super_methods
@dataclass_json
@dataclass
class TransferRequest:
    sender: str
    message: TransferRequestMessage
    message_signature: str

    def __post_init__(self):
        self.validation_errors: list[str] = []

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

        return self.is_signature_valid() and self.is_amount_valid() and self.is_balance_key_valid()

    def is_signature_valid(self) -> bool:
        if not is_valid_signature(self.sender, self.message.get_normalized(), self.message_signature):
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

    def is_balance_key_valid(self) -> bool:
        if self.message.balance_key != get_blockchain().get_account_balance_lock(self.sender):
            self.add_validation_error('Balance key does not match balance lock')
            return False

        return True


# TODO(dmu) LOW: Find a better way to avoid circular imports
from ..blockchain import get_blockchain  # noqa: E402,I202
