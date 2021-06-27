import logging
import warnings
from typing import Generator, Optional

from more_itertools import always_reversible, ilen

from thenewboston_node.business_logic.models.blockchain_state import BlockchainState

logger = logging.getLogger(__name__)


class BlockchainStateMixin:

    def persist_blockchain_state(self, account_root_file: BlockchainState):
        raise NotImplementedError('Must be implemented in a child class')

    def yield_blockchain_states(self) -> Generator[BlockchainState, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_blockchain_states_count(self) -> int:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn('Using low performance implementation of get_account_root_file_count() method (override it)')
        return ilen(self.yield_blockchain_states())

    def yield_blockchain_states_reversed(self) -> Generator[BlockchainState, None, None]:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn(
            'Using low performance implementation of yield_blockchain_states_reversed() method (override it)'
        )
        yield from always_reversible(self.yield_blockchain_states())

    def add_blockchain_state(self, blockchain_state: BlockchainState):
        blockchain_state.validate(is_initial=blockchain_state.is_initial())
        self.persist_blockchain_state(blockchain_state)

    def get_first_blockchain_state(self) -> Optional[BlockchainState]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.yield_blockchain_states())
        except StopIteration:
            return None

    def get_last_blockchain_state(self) -> Optional[BlockchainState]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.yield_blockchain_states_reversed())
        except StopIteration:
            return None

    def has_blockchain_states(self):
        # Override this method if a particular blockchain implementation can provide a high performance
        return self.get_first_blockchain_state() is not None
