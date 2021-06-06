import logging
from copy import deepcopy
from typing import Optional

from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.core.logging import timeit_method
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)


class AccountStateMixin:

    def yield_known_accounts(self):
        known_accounts = set()
        for block in self.yield_blocks_till_snapshot():  # type: ignore
            block_accounts = set(block.message.updated_account_states.keys())
            new_accounts = block_accounts - known_accounts
            known_accounts |= new_accounts
            for new_account in new_accounts:
                yield new_account

        last_account_root_file = self.get_first_blockchain_state()  # type: ignore
        account_root_file_accounts = last_account_root_file.account_states.keys()
        new_accounts = account_root_file_accounts - known_accounts
        known_accounts |= new_accounts
        for new_account in new_accounts:
            yield new_account

    def get_account_state_attribute_value(self, account: hexstr, attribute: str, on_block_number: int):
        if on_block_number < -1:
            raise ValueError('block_number must be greater or equal to -1')
        elif on_block_number > self.get_current_block_number():  # type: ignore
            raise ValueError('block_number must be less than current block number')

        account_state = self._get_account_state_from_block(account, on_block_number, attribute)
        if account_state:
            return account_state.get_attribute_value(attribute, account)

        blockchain_state = self.get_closest_blockchain_state_snapshot(on_block_number + 1)
        assert blockchain_state

        return blockchain_state.get_account_state_attribute_value(account, attribute)

    def get_account_balance(self, account: hexstr, on_block_number: int) -> int:
        return self.get_account_state_attribute_value(account, 'balance', on_block_number)

    def get_account_current_balance(self, account: str) -> int:
        return self.get_account_balance(account, self.get_current_block_number())  # type: ignore

    def get_account_balance_lock(self, account: hexstr, on_block_number: int) -> hexstr:
        return self.get_account_state_attribute_value(account, 'balance_lock', on_block_number)

    def get_account_current_balance_lock(self, account: hexstr) -> hexstr:
        return self.get_account_balance_lock(account, self.get_current_block_number())  # type: ignore

    def get_node(self, account: hexstr, on_block_number: int):
        return self.get_account_state_attribute_value(account, 'node', on_block_number)  # type: ignore

    def get_current_node(self, account: hexstr):
        return self.get_node(account, self.get_current_block_number())  # type: ignore

    def get_account_state(self, account: hexstr) -> AccountState:
        block_number = self.get_current_block_number()  # type: ignore
        return AccountState(
            balance=self.get_account_balance(account, block_number),
            balance_lock=self.get_account_balance_lock(account, block_number),
            node=self.get_node(account, block_number),
        )

    @timeit_method()
    def _get_account_state_from_block(
        self,
        account: str,
        block_number: int,
        expected_attribute: str,
    ) -> Optional[AccountState]:
        for block in self.yield_blocks_till_snapshot(block_number):  # type: ignore
            account_state = block.message.get_account_state(account)
            if account_state is not None:
                value = getattr(account_state, expected_attribute, None)
                if value is not None:
                    return account_state

        return None

    def get_expected_block_identifier(self, block_number: int) -> Optional[str]:
        """
        Return expected block identifier (take from previous block message hash or account root file)
        for the `block_number` (from 0 to head block number + 1 inclusive).

        To be used for validation of existing and generation of new blocks.
        """
        if block_number < 0:
            raise ValueError('block_number must be greater or equal to 0')

        account_root_file = self.get_closest_blockchain_state_snapshot(block_number)
        if account_root_file is None:
            logger.warning('Block number %s is beyond known account root files', block_number)
            return None

        if block_number == 0:
            assert account_root_file.is_initial()
            return account_root_file.get_next_block_identifier()

        prev_block_number = block_number - 1
        if prev_block_number == account_root_file.last_block_number:
            return account_root_file.get_next_block_identifier()

        block = self.get_block_by_number(prev_block_number)  # type: ignore
        assert block is not None
        return block.message_hash

    def get_closest_blockchain_state_snapshot(self,
                                              excludes_block_number: Optional[int] = None
                                              ) -> Optional[BlockchainState]:
        """
        Return the latest account root file that does not include `excludes_block_number` (
        head block by default thus the latest account root file, use -1 for getting initial account root file).
        None is returned if `excludes_block_number` block is not included in even in the earliest account
        root file (this may happen for partial blockchains that cut off genesis and no initial root account file)
        """
        if excludes_block_number is not None and excludes_block_number < -1:
            raise ValueError('before_block_number_inclusive must be greater or equal to -1')

        if excludes_block_number is None:
            logger.debug('excludes_block_number is None: returning the last account root file')
            account_root_file = self.get_last_blockchain_state()  # type: ignore
        elif excludes_block_number == -1:
            logger.debug('excludes_block_number == -1: initial account root file is requested (not just first)')
            first_account_root_file = self.get_first_blockchain_state()  # type: ignore
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

                for attribute in AccountState.__dataclass_fields__.keys():  # type: ignore
                    value = getattr(block_account_state, attribute)
                    if value is not None:
                        setattr(blockchain_state_account_state, attribute, deepcopy(value))

        if block is not None:
            blockchain_state.last_block_number = block.message.block_number
            blockchain_state.last_block_identifier = block.message.block_identifier
            blockchain_state.last_block_timestamp = block.message.timestamp
            blockchain_state.next_block_identifier = block.message_hash

        return blockchain_state
