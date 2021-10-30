import logging
from typing import Generator, Optional

from more_itertools import ilen

from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.models import Node
from thenewboston_node.core.utils.types import hexstr

from .base import BaseMixin

logger = logging.getLogger(__name__)


class NetworkMixin(BaseMixin):

    def get_node_by_identifier(self, identifier: hexstr, on_block_number: Optional[int] = None) -> Optional[Node]:
        if on_block_number is None:
            on_block_number = self.get_last_block_number()
        return self.get_account_state_attribute_value(identifier, 'node', on_block_number)

    def get_nodes_count(self, block_number: Optional[int] = None) -> int:
        return ilen(self.yield_nodes(block_number=block_number))

    def yield_nodes(self, block_number: Optional[int] = None) -> Generator[Node, None, None]:
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

    def get_primary_validator(self, for_block_number: Optional[int] = None) -> Optional[Node]:
        if for_block_number is None:
            for_block_number = self.get_next_block_number()

        # We get last_block_number and blockchain_state here to avoid race conditions. Do not change it
        last_block_number = self.get_last_block_number()
        blockchain_state = self.get_blockchain_state_by_block_number(
            last_block_number, inclusive=last_block_number > -1
        )
        known_pv_schedule_accounts = set()

        logger.debug('Traverse blocks until we find a PV schedule that includes the desired block_number')
        for block in self.yield_blocks_slice_reversed(last_block_number, blockchain_state.last_block_number):
            for account_number, account_state in block.yield_account_states():
                if account_number in known_pv_schedule_accounts:
                    raise AssertionError('Should never get here')

                pv_schedule = account_state.primary_validator_schedule
                if pv_schedule:
                    known_pv_schedule_accounts.add(account_number)
                    if pv_schedule.is_block_number_included(for_block_number):
                        return self.get_node_by_identifier(account_number)

        # TODO(dmu) HIGH: Once we have more accounts this method will become slow. We need to optimize it
        #                 by caching
        for account_number, account_state in blockchain_state.yield_account_states():
            if account_number in known_pv_schedule_accounts:
                continue  # Schedule was overwritten with blocks

            known_pv_schedule_accounts.add(account_number)
            pv_schedule = account_state.primary_validator_schedule
            if pv_schedule and pv_schedule.is_block_number_included(for_block_number):
                return self.get_node_by_identifier(account_number)

        return None

    def get_node_role(self, identifier: hexstr) -> Optional[NodeRole]:
        last_block_number = self.get_last_block_number()
        node = self.get_node_by_identifier(identifier, last_block_number)

        if node is None:
            return None

        schedule = self.get_primary_validator_schedule(identifier, last_block_number)

        next_block_number = last_block_number + 1
        if schedule is None or schedule.is_schedule_in_past(next_block_number):
            return NodeRole.REGULAR_NODE

        if schedule.is_schedule_at_present(next_block_number):
            return NodeRole.PRIMARY_VALIDATOR

        assert schedule.is_schedule_in_future(next_block_number)
        return NodeRole.CONFIRMATION_VALIDATOR
