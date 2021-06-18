import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import hash_normalized_dict
from thenewboston_node.core.utils.types import hexstr

from .account_state import AccountState
from .base import BaseDataclass
from .mixins.compactable import MessagpackCompactableMixin
from .mixins.normalizable import NormalizableMixin

logger = logging.getLogger(__name__)


@dataclass
class BlockchainState(MessagpackCompactableMixin, NormalizableMixin, BaseDataclass):
    """Historical snapshot of all account balances at any point in time"""

    account_states: dict[hexstr, AccountState]
    """Map like {"account_number": `AccountState`_, ...}"""

    last_block_number: Optional[int] = None
    """Block number at which snapshot was taken"""

    # TODO(dmu) MEDIUM: Do we really need last_block_identifier?
    last_block_identifier: Optional[hexstr] = None
    """Block identifier at which snapshot was taken"""

    last_block_timestamp: Optional[datetime] = None
    next_block_identifier: Optional[hexstr] = None

    def get_account_state(self, account: hexstr) -> Optional[AccountState]:
        return self.account_states.get(account)

    def get_account_state_attribute_value(self, account: hexstr, attribute: str):
        account_state = self.get_account_state(account)
        if account_state is None:
            from thenewboston_node.business_logic.utils.blockchain import get_attribute_default_value
            return get_attribute_default_value(attribute, account)

        return account_state.get_attribute_value(attribute, account)

    def get_account_balance(self, account: hexstr) -> int:
        return self.get_account_state_attribute_value(account, 'balance')

    def get_account_balance_lock(self, account: hexstr) -> str:
        return self.get_account_state_attribute_value(account, 'balance_lock')

    def get_node(self, account: hexstr):
        return self.get_account_state_attribute_value(account, 'node')

    def get_next_block_number(self) -> int:
        last_block_number = self.last_block_number
        return 0 if last_block_number is None else last_block_number + 1

    def get_next_block_identifier(self) -> hexstr:
        next_block_identifier = self.next_block_identifier
        if next_block_identifier:
            return next_block_identifier

        return self.get_hash()  # initial account root file case

    def get_hash(self):
        return hash_normalized_dict(self.get_normalized())

    def is_initial(self) -> bool:
        return (
            self.last_block_number is None and self.last_block_identifier is None and
            self.next_block_identifier is None and self.last_block_timestamp is None
        )

    @validates('account root file')
    def validate(self, is_initial=False):
        self.validate_attributes(is_initial=is_initial)
        self.validate_accounts()

    @validates('account root file attributes', is_plural_target=True)
    def validate_attributes(self, is_initial=False):
        self.validate_last_block_number(is_initial)
        self.validate_last_block_identifier(is_initial)
        self.validate_last_block_timestamp(is_initial)
        self.validate_next_block_identifier(is_initial)

    @validates('account root file last_block_number')
    def validate_last_block_number(self, is_initial):
        if is_initial:
            if self.last_block_number is not None:
                raise ValidationError(
                    'Account root file last block number must not be set for initial account root file'
                )
        else:
            if not isinstance(self.last_block_number, int):
                raise ValidationError('Account root file last block number must be an integer')
            if self.last_block_number < 0:
                raise ValidationError('Account root file last block number must be a non-negative integer')

    @validates('account root file last_block_identifier')
    def validate_last_block_identifier(self, is_initial):
        if is_initial:
            if self.last_block_identifier is not None:
                raise ValidationError(
                    'Account root file last block identifier must not be set for initial account root file'
                )
        else:
            if not isinstance(self.last_block_identifier, str):
                raise ValidationError('Account root file last block identifier must be a string')

    @validates('account root file last_block_timestamp')
    def validate_last_block_timestamp(self, is_initial):
        if is_initial:
            if self.last_block_timestamp is not None:
                raise ValidationError(
                    'Account root file last block timestamp must not be set for initial account root file'
                )
        else:
            timestamp = self.last_block_timestamp
            if timestamp is None:
                raise ValidationError('Account root file last block timestamp must be set')

            if not isinstance(timestamp, datetime):
                raise ValidationError('Account root file last block timestamp must be datetime type')

            if timestamp.tzinfo is not None:
                raise ValidationError(
                    'Account root file last block timestamp must be naive datetime (UTC timezone implied)'
                )

    @validates('account root file next_block_identifier')
    def validate_next_block_identifier(self, is_initial):
        if is_initial:
            if self.next_block_identifier is not None:
                raise ValidationError(
                    'Account root file next block identifier must not be set for initial account root file'
                )
        else:
            if not isinstance(self.next_block_identifier, str):
                raise ValidationError('Account root file next block identifier must be a string')

    @validates('account root file accounts', is_plural_target=True)
    def validate_accounts(self):
        for account, balance in self.account_states.items():
            with validates(f'account root file account {account}'):
                if not isinstance(account, str):
                    raise ValidationError('Account root file account number must be a string')
                balance.validate()
