from dataclasses import dataclass

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.account import get_account_balance
from thenewboston_node.business_logic.account import get_account_balance_lock
from thenewboston_node.business_logic.message import is_valid_message_signature
from thenewboston_node.business_logic.message import make_signable_message
from thenewboston_node.core.utils.constants import SENTINEL

from .transfer_request_message import TransferRequestMessage


@dataclass_json
@dataclass
class TransferRequest:
    sender: str
    message: TransferRequestMessage
    signature: str

    def __post_init__(self):
        self.validation_errors: list[str] = []

    def add_validation_error(self, error_message: str):
        self.validation_errors.append(error_message)

    def is_valid(self) -> bool:
        if self.validation_errors:
            self.validation_errors = []

        return self.is_signature_valid() and self.is_amount_valid() and self.is_balance_key_valid()

    def get_signable_message(self) -> bytes:
        message_dict = self.message.to_dict()  # type: ignore

        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in signable message
        txs = message_dict['txs']
        for tx in txs:
            fee_value = tx.get('fee', SENTINEL)
            if fee_value is None:
                del tx['fee']

        return make_signable_message(message_dict)

    def is_signature_valid(self) -> bool:
        if not is_valid_message_signature(self.sender, self.get_signable_message(), self.signature):
            self.add_validation_error('Message signature is invalid')
            return False

        return True

    def is_amount_valid(self) -> bool:
        balance = get_account_balance(self.sender)
        if balance is None:
            self.add_validation_error('Account balance is not found')
            return False

        if self.message.total_amount > balance:
            self.add_validation_error('Transaction total amount is greater than account balance')
            return False

        return True

    def is_balance_key_valid(self) -> bool:
        if self.message.balance_key != get_account_balance_lock(self.sender):
            self.add_validation_error('Balance key does not match balance lock')
            return False

        return True
