from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.cryptography import hash_normalized_dict, normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .account_balance import AccountBalance


@fake_super_methods
@dataclass_json
@dataclass
class AccountRootFile:
    accounts: dict[str, AccountBalance]
    last_block_number: Optional[int] = None

    # TODO(dmu) MEDIUM: Do we really need last_block_identifier?
    last_block_identifier: Optional[str] = None
    next_block_identifier: Optional[str] = None

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()

        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        for attr in ('last_block_number', 'last_block_identifier', 'next_block_identifier'):
            value = dict_.get(attr, SENTINEL)
            if value is None:
                del dict_[attr]

        return dict_

    def get_balance(self, account: str) -> Optional[AccountBalance]:
        return self.accounts.get(account)

    def get_balance_value(self, account: str) -> Optional[int]:
        balance = self.get_balance(account)
        if balance is not None:
            return balance.balance

        return None

    def get_balance_lock(self, account: str) -> str:
        balance = self.get_balance(account)
        if balance is not None:
            return balance.balance_lock

        return account

    def get_next_block_number(self) -> int:
        last_block_number = self.last_block_number
        return 0 if last_block_number is None else last_block_number + 1

    def get_next_block_identifier(self) -> str:
        next_block_identifier = self.next_block_identifier
        if next_block_identifier:
            return next_block_identifier

        return hash_normalized_dict(self.get_normalized())

    def get_normalized(self) -> bytes:
        return normalize_dict(self.to_dict())  # type: ignore

    def is_initial(self) -> bool:
        return (
            self.last_block_number is None and self.last_block_identifier is None and
            self.next_block_identifier is None
        )

    def validate(self, is_initial=False):
        self.validate_accounts()
        if is_initial:
            if self.last_block_number is not None:
                ValidationError('Last block number must not be set for initial account root file')
            if self.last_block_identifier is not None:
                ValidationError('Last block identifier must not be set for initial account root file')
            if self.next_block_identifier is not None:
                ValidationError('Next block identifier must not be set for initial account root file')
        else:
            if not isinstance(self.last_block_number, int):
                ValidationError('Last block number must be an integer')
            if not isinstance(self.last_block_identifier, str):
                ValidationError('Last block identifier must be a string')
            if not isinstance(self.next_block_identifier, str):
                ValidationError('Next block identifier must be a string')

    def validate_accounts(self):
        for account, balance in self.accounts.items():
            if not isinstance(account, str):
                raise ValidationError('Account number must be a string')

            balance.validate()
