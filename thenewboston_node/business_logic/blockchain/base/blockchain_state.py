import logging
import warnings
from typing import Generator, Optional

from more_itertools import always_reversible, ilen

from thenewboston_node.business_logic.models.blockchain_state import BlockchainState

logger = logging.getLogger(__name__)


class BlockchainStateMixin:

    def persist_blockchain_state(self, account_root_file: BlockchainState):
        raise NotImplementedError('Must be implemented in a child class')

    def iter_account_root_files(self) -> Generator[BlockchainState, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_account_root_file_count(self) -> int:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn('Using low performance implementation of get_account_root_file_count() method (override it)')
        return ilen(self.iter_account_root_files())

    def iter_account_root_files_reversed(self) -> Generator[BlockchainState, None, None]:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn(
            'Using low performance implementation of iter_account_root_files_reversed() method (override it)'
        )
        yield from always_reversible(self.iter_account_root_files())

    # * Base methods
    # ** Account root files related base methods
    def add_blockchain_state(self, state: BlockchainState):
        state.validate(is_initial=state.is_initial())
        self.persist_blockchain_state(state)

    def get_first_account_root_file(self) -> Optional[BlockchainState]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.iter_account_root_files())
        except StopIteration:
            return None

    def get_last_account_root_file(self) -> Optional[BlockchainState]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.iter_account_root_files_reversed())
        except StopIteration:
            return None
