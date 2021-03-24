import logging
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.cryptography import hash_normalized_dict, normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .account_balance import AccountBalance

logger = logging.getLogger(__name__)
validation_logger = logging.getLogger(__name__ + '.validation_logger')


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
            return balance.value

        return None

    def get_balance_lock(self, account: str) -> str:
        balance = self.get_balance(account)
        if balance is not None:
            return balance.lock

        return account

    def get_next_block_number(self) -> int:
        last_block_number = self.last_block_number
        return 0 if last_block_number is None else last_block_number + 1

    def get_next_block_identifier(self) -> str:
        next_block_identifier = self.next_block_identifier
        if next_block_identifier:
            return next_block_identifier

        return self.get_hash()  # initial account root file case

    def get_normalized(self) -> bytes:
        return normalize_dict(self.to_dict())  # type: ignore

    def get_hash(self):
        return hash_normalized_dict(self.get_normalized())

    def is_initial(self) -> bool:
        return (
            self.last_block_number is None and self.last_block_identifier is None and
            self.next_block_identifier is None
        )

    def validate(self, is_initial=False):
        validation_logger.debug('Validating account root file')
        if is_initial:
            if self.last_block_number is not None:
                raise ValidationError(
                    'Account root file last block number must not be set for initial account root file'
                )
            validation_logger.debug(
                'Account root file last block number is not set for the initial account root file (as expected)'
            )
            if self.last_block_identifier is not None:
                raise ValidationError(
                    'Account root file last block identifier must not be set for initial account root file'
                )
            validation_logger.debug(
                'Account root file last block identifier is not set for the initial account root file (as expected)'
            )
            if self.next_block_identifier is not None:
                raise ValidationError(
                    'Account root file next block identifier must not be set for initial account root file'
                )
            validation_logger.debug(
                'Account root file next block identifier is not set for the initial account root file (as expected)'
            )
        else:
            if not isinstance(self.last_block_number, int):
                raise ValidationError('Account root file last block number must be an integer')
            validation_logger.debug('Account root file last block number is an integer for account root file')
            if not isinstance(self.last_block_identifier, str):
                raise ValidationError('Account root file last block identifier must be a string')
            validation_logger.debug('Account root file last block identifier is a string for account root file')
            if not isinstance(self.next_block_identifier, str):
                raise ValidationError('Account root file next block identifier must be a string')
            validation_logger.debug('Account root file next block identifier is a string for account root file')
        self.validate_accounts()
        validation_logger.debug('Account root file is valid')

    def validate_accounts(self):
        validation_logger.debug('Validating account root file accounts')
        for account, balance in self.accounts.items():
            validation_logger.debug('Validating Account root file account %s', account)
            if not isinstance(account, str):
                raise ValidationError('Account root file account number must be a string')
            validation_logger.debug('Account root file account number is a string')

            balance.validate()
            validation_logger.debug('Account root file account %s is valid', account)
        validation_logger.debug('Account root file accounts are valid')
