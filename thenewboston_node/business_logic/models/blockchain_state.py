import logging
from dataclasses import dataclass, field
from typing import Any, Generator, Optional, Type, TypeVar

from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.misc import if_none
from thenewboston_node.core.utils.types import hexstr

from .account_state import AccountState
from .base import BaseDataclass
from .blockchain_state_message import BlockchainStateMessage
from .mixins.compactable import MessagpackCompactableMixin
from .mixins.metadata import MetadataMixin
from .mixins.normalizable import NormalizableMixin
from .mixins.signable import SignableMixin

T = TypeVar('T', bound='BlockchainState')

logger = logging.getLogger(__name__)


@revert_docstring
@dataclass
@cover_docstring
class BlockchainState(SignableMixin, MetadataMixin, MessagpackCompactableMixin, NormalizableMixin, BaseDataclass):
    message: BlockchainStateMessage

    meta: Optional[dict[str, Any]] = field(  # noqa: A003
        default=None, metadata={
            'is_serializable': False,
        }
    )

    @classmethod
    def create_from_account_root_file(cls: Type[T], account_root_file_dict, signer) -> T:
        account_states = {}
        for account_number, content in account_root_file_dict.items():
            balance_lock = content.get('balance_lock')
            account_states[account_number] = AccountState(
                balance=content['balance'], balance_lock=None if balance_lock == account_number else balance_lock
            )
        return cls(message=BlockchainStateMessage(account_states=account_states), signer=signer)

    def yield_account_states(self) -> Generator[tuple[hexstr, AccountState], None, None]:
        yield from self.message.account_states.items()

    def yield_nodes(self):
        for account_number, account_state in self.yield_account_states():
            node = account_state.node
            if node:
                assert node.identifier == account_number
                yield node

    def get_account_state(self, account: hexstr) -> Optional[AccountState]:
        return self.message.account_states.get(account)

    def set_account_state(self, account: hexstr, account_state: AccountState):
        self.message.account_states[account] = account_state

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

    @property
    def last_block_number(self) -> int:
        return if_none(self.message.last_block_number, -1)

    @last_block_number.setter
    def last_block_number(self, value):
        self.message.last_block_number = value

    @property
    def last_block_identifier(self):
        return self.message.last_block_identifier

    @last_block_identifier.setter
    def last_block_identifier(self, value):
        self.message.last_block_identifier = value

    @property
    def last_block_timestamp(self):
        return self.message.last_block_timestamp

    @last_block_timestamp.setter
    def last_block_timestamp(self, value):
        self.message.last_block_timestamp = value

    @property
    def account_states(self):
        return self.message.account_states

    @account_states.setter
    def account_states(self, value):
        self.message.account_states = value

    @property
    def next_block_number(self) -> int:
        return self.last_block_number + 1

    @property
    def next_block_identifier(self):
        next_block_identifier = self.message.next_block_identifier
        if next_block_identifier:
            return next_block_identifier

        return self.message.get_hash()  # initial blockchain state case

    @next_block_identifier.setter
    def next_block_identifier(self, value):
        self.message.next_block_identifier = value

    def is_initial(self) -> bool:
        return (
            self.message.last_block_number is None and self.message.last_block_identifier is None and
            self.message.next_block_identifier is None and self.message.last_block_timestamp is None
        )

    def validate(self, is_initial=False):
        self.message.validate(is_initial=is_initial)
