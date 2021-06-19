import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from thenewboston_node.business_logic.validators import (
    validate_gte_value, validate_is_none, validate_not_none, validate_type
)
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

        return self.get_hash()  # initial blockchain state case

    def get_hash(self):
        return hash_normalized_dict(self.get_normalized())

    def is_initial(self) -> bool:
        return (
            self.last_block_number is None and self.last_block_identifier is None and
            self.next_block_identifier is None and self.last_block_timestamp is None
        )

    @validates('blockchain state')
    def validate(self, is_initial=False):
        self.validate_attributes(is_initial=is_initial)
        self.validate_accounts()

    @validates('blockchain state attributes', is_plural_target=True)
    def validate_attributes(self, is_initial=False):
        self.validate_last_block_number(is_initial)
        self.validate_last_block_identifier(is_initial)
        self.validate_last_block_timestamp(is_initial)
        self.validate_next_block_identifier(is_initial)

    @validates('blockchain state last_block_number')
    def validate_last_block_number(self, is_initial):
        if is_initial:
            validate_is_none(f'Initial {self.humanized_class_name} last_block_number', self.last_block_number)
        else:
            validate_type(f'{self.humanized_class_name} last_block_number', self.last_block_number, int)
            validate_gte_value(f'{self.humanized_class_name} last_block_number', self.last_block_number, 0)

    @validates('blockchain state last_block_identifier')
    def validate_last_block_identifier(self, is_initial):
        if is_initial:
            validate_is_none(f'Initial {self.humanized_class_name} last_block_identifier', self.last_block_identifier)
        else:
            validate_type(f'{self.humanized_class_name} last_block_identifier', self.last_block_identifier, str)

    @validates('blockchain state last_block_timestamp')
    def validate_last_block_timestamp(self, is_initial):
        timestamp = self.last_block_timestamp
        if is_initial:
            validate_is_none(f'Initial {self.humanized_class_name} last_block_timestamp', timestamp)
        else:
            validate_not_none(f'{self.humanized_class_name} last_block_timestamp', timestamp)
            validate_type(f'{self.humanized_class_name} last_block_timestamp', timestamp, datetime)
            validate_is_none(f'{self.humanized_class_name} last_block_timestamp', timestamp.tzinfo)

    @validates('blockchain state next_block_identifier')
    def validate_next_block_identifier(self, is_initial):
        if is_initial:
            validate_is_none(f'Initial {self.humanized_class_name} next_block_identifier', self.next_block_identifier)
        else:
            validate_type(f'{self.humanized_class_name} next_block_identifier', self.next_block_identifier, str)

    @validates('blockchain state accounts', is_plural_target=True)
    def validate_accounts(self):
        for account, balance in self.account_states.items():
            with validates(f'blockchain state account {account}'):
                validate_type(f'{self.humanized_class_name} account', account, str)
                balance.validate()
