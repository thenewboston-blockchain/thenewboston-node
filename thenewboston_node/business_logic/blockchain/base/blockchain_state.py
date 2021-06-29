import logging
import warnings
from copy import deepcopy
from typing import Generator, Optional

from more_itertools import always_reversible, ilen

from thenewboston_node.business_logic.models import AccountState, BlockchainState

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

    def get_closest_blockchain_state_snapshot(self,
                                              excludes_block_number: Optional[int] = None
                                              ) -> Optional[BlockchainState]:
        if excludes_block_number is not None and excludes_block_number < -1:
            raise ValueError('before_block_number_inclusive must be greater or equal to -1')

        if excludes_block_number is None:
            logger.debug('excludes_block_number is None: returning the last account root file')
            account_root_file = self.get_last_blockchain_state()
        elif excludes_block_number == -1:
            logger.debug('excludes_block_number == -1: initial account root file is requested (not just first)')
            first_account_root_file = self.get_first_blockchain_state()
            if first_account_root_file and first_account_root_file.is_initial():
                logger.debug('Returning first account root file (which is also an initial account root file)')
                account_root_file = first_account_root_file
            else:
                logger.warning('Initial account root file is not found')
                account_root_file = None
        else:
            logger.debug(
                'excludes_block_number == %s: intermediate account root file is requested', excludes_block_number
            )
            for account_root_file in self.yield_blockchain_states_reversed():  # type: ignore
                logger.debug(
                    'Traversing account root file with last_block_number=%s', account_root_file.last_block_number
                )
                last_block_number = account_root_file.last_block_number
                if last_block_number is None:
                    assert account_root_file.is_initial()
                    logger.debug('Encountered initial account root file')
                    break

                if last_block_number < excludes_block_number:
                    logger.debug(
                        'Found account root file that does not include block number %s (last_block_number=%s)',
                        excludes_block_number, last_block_number
                    )
                    break
            else:
                logger.warning('Requested account root file is not found (partial blockchain is unexpectedly short)')
                account_root_file = None

        if account_root_file is None:
            logger.warning('Could not find account root file that excludes block number %s', excludes_block_number)
            return None

        return deepcopy(account_root_file)

    def snapshot_blockchain_state(self):
        last_block = self.get_last_block()  # type: ignore
        if last_block is None:
            logger.warning('Blocks are not found: making account root file does not make sense')
            return None

        last_account_root_file = self.get_last_blockchain_state()  # type: ignore
        assert last_account_root_file is not None

        if not last_account_root_file.is_initial():
            assert last_account_root_file.last_block_number is not None
            if last_block.message.block_number <= last_account_root_file.last_block_number:
                logger.debug('The last block is already included in the last account root file')
                return None

        account_root_file = self.generate_blockchain_state()
        self.add_blockchain_state(account_root_file)

    def generate_blockchain_state(self, last_block_number: Optional[int] = None) -> BlockchainState:
        last_blockchain_state_snapshot = self.get_closest_blockchain_state_snapshot(last_block_number)
        assert last_blockchain_state_snapshot is not None
        logger.debug(
            'Generating blockchain state snapshot based on blockchain state with last_block_number=%s',
            last_blockchain_state_snapshot.last_block_number
        )

        blockchain_state = deepcopy(last_blockchain_state_snapshot)
        account_states = blockchain_state.account_states

        block = None
        for block in self.yield_blocks_from(blockchain_state.get_next_block_number()):  # type: ignore
            if last_block_number is not None and block.message.block_number > last_block_number:
                logger.debug('Traversed all blocks of interest')
                break

            logger.debug('Traversing block number %s', block.message.block_number)
            for account_number, block_account_state in block.message.updated_account_states.items():
                logger.debug('Found %s account state: %s', account_number, block_account_state)
                blockchain_state_account_state = account_states.get(account_number)
                if blockchain_state_account_state is None:
                    logger.debug('Account %s is met for the first time (empty lock is expected)', account_number)
                    assert block_account_state.balance_lock is None
                    blockchain_state_account_state = AccountState()
                    account_states[account_number] = blockchain_state_account_state

                for attribute in AccountState.get_field_names():  # type: ignore
                    value = getattr(block_account_state, attribute)
                    if value is not None:
                        setattr(blockchain_state_account_state, attribute, deepcopy(value))

        if block is not None:
            blockchain_state.last_block_number = block.message.block_number
            blockchain_state.last_block_identifier = block.message.block_identifier
            blockchain_state.last_block_timestamp = block.message.timestamp
            blockchain_state.next_block_identifier = block.hash

        return blockchain_state
