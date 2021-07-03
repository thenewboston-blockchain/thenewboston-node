import logging
from typing import Optional

from thenewboston_node.business_logic.models import Node
from thenewboston_node.core.utils.types import hexstr

from .base import BaseMixin

logger = logging.getLogger(__name__)


class NetworkMixin(BaseMixin):

    def get_node_by_identifier(self, identifier: hexstr, on_block_number: Optional[int] = None) -> Optional[Node]:
        if on_block_number is None:
            on_block_number = self.get_last_block_number()
        return self.get_account_state_attribute_value(identifier, 'node', on_block_number)

    def yield_nodes(self, block_number: Optional[int] = None):
        known_accounts = set()
        for account_number, account_state in self.yield_account_states(from_block_number=block_number):
            node = account_state.node
            if not node:
                continue

            if account_number in known_accounts:
                continue

            known_accounts.add(account_number)
            yield node

    def has_nodes(self):
        return any(self.yield_nodes())
