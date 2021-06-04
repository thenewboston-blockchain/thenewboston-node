import copy
import logging
from typing import Optional

from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.core.logging import timeit_method

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

        last_account_root_file = self.get_first_account_root_file()  # type: ignore
        account_root_file_accounts = last_account_root_file.account_states.keys()
        new_accounts = account_root_file_accounts - known_accounts
        known_accounts |= new_accounts
        for new_account in new_accounts:
            yield new_account

    def validate_before_block_number(self, before_block_number: Optional[int]) -> int:
        next_block_number = self.get_next_block_number()  # type: ignore
        if before_block_number is None:
            return next_block_number
        elif before_block_number < 0:
            raise ValueError('block_number must be greater or equal to 0')
        elif before_block_number > next_block_number:
            raise ValueError('block_number must be less or equal to next block number')

        return before_block_number

    def get_account_balance(self, account: str, before_block_number: Optional[int] = None) -> Optional[int]:
        """
        Return balance value before `before_block_number` is applied. If `before_block_number` is not specified it
        defaults to the next block number.
        """
        block_number = self.validate_before_block_number(before_block_number) - 1
        balance = self._get_account_balance_from_block(account, block_number)
        if balance is None:
            balance = self._get_account_balance_from_account_root_file(account, block_number)

        return balance

    @timeit_method()
    def get_account_balance_lock(self, account: str, before_block_number: Optional[int] = None) -> str:
        """
        Return balance lock before `before_block_number` is applied. If `before_block_number` is not specified it
        defaults to the next block number.
        """
        block_number = self.validate_before_block_number(before_block_number) - 1
        lock = self._get_account_lock_from_block(account, block_number)
        if lock:
            return lock

        lock = self._get_account_lock_from_account_root_file(account, block_number)
        return account if lock is None else lock

    def get_account_state(self, account: str) -> AccountState:
        return AccountState(
            balance=self.get_account_balance(account) or 0, balance_lock=self.get_account_balance_lock(account)
        )

    @timeit_method()
    def _get_account_lock_from_block(self, account: str, block_number: Optional[int] = None) -> Optional[str]:
        balance = self._get_account_state_from_block(account, block_number, expected_attribute='balance_lock')
        return None if balance is None else balance.balance_lock

    def _get_account_lock_from_account_root_file(self,
                                                 account: str,
                                                 block_number: Optional[int] = None) -> Optional[str]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.balance_lock

    def _get_account_balance_from_block(self, account: str, block_number: Optional[int] = None) -> Optional[int]:
        account_state = self._get_account_state_from_block(account, block_number, expected_attribute='balance')
        return None if account_state is None else account_state.balance

    @timeit_method()
    def _get_account_state_from_block(
        self,
        account: str,
        block_number: Optional[int] = None,
        expected_attribute: Optional[str] = None,
    ) -> Optional[AccountState]:
        for block in self.yield_blocks_till_snapshot(block_number):  # type: ignore
            account_state = block.message.get_account_state(account)
            if account_state is not None:
                if expected_attribute is None:
                    return account_state
                else:
                    value = getattr(account_state, expected_attribute, None)
                    if value is not None:
                        return account_state

        return None

    def _get_account_balance_from_account_root_file(self,
                                                    account: str,
                                                    block_number: Optional[int] = None) -> Optional[int]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.balance

    def _get_balance_from_account_root_file(self,
                                            account: str,
                                            block_number: Optional[int] = None) -> Optional[AccountState]:
        excludes_block_number = None if block_number is None else block_number + 1
        account_root_file = self.get_closest_account_root_file(excludes_block_number)
        assert account_root_file
        return account_root_file.get_account_state(account)

    def get_expected_block_identifier(self, block_number: int) -> Optional[str]:
        """
        Return expected block identifier (take from previous block message hash or account root file)
        for the `block_number` (from 0 to head block number + 1 inclusive).

        To be used for validation of existing and generation of new blocks.
        """
        if block_number < 0:
            raise ValueError('block_number must be greater or equal to 0')

        account_root_file = self.get_closest_account_root_file(block_number)
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

    def get_closest_account_root_file(self, excludes_block_number: Optional[int] = None) -> Optional[BlockchainState]:
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
            account_root_file = self.get_last_account_root_file()  # type: ignore
        elif excludes_block_number == -1:
            logger.debug('excludes_block_number == -1: initial account root file is requested (not just first)')
            first_account_root_file = self.get_first_account_root_file()  # type: ignore
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
            for account_root_file in self.iter_account_root_files_reversed():  # type: ignore
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

        return copy.deepcopy(account_root_file)

    def snapshot_blockchain_state(self):
        last_block = self.get_last_block()  # type: ignore
        if last_block is None:
            logger.warning('Blocks are not found: making account root file does not make sense')
            return None

        last_account_root_file = self.get_last_account_root_file()  # type: ignore
        assert last_account_root_file is not None

        if not last_account_root_file.is_initial():
            assert last_account_root_file.last_block_number is not None
            if last_block.message.block_number <= last_account_root_file.last_block_number:
                logger.debug('The last block is already included in the last account root file')
                return None

        account_root_file = self.generate_account_root_file()
        self.add_blockchain_state(account_root_file)

    def generate_account_root_file(self, last_block_number: Optional[int] = None) -> BlockchainState:
        last_account_root_file = self.get_closest_account_root_file(last_block_number)
        assert last_account_root_file is not None
        logger.debug(
            'Generating account root file based on account root file with last_block_number=%s',
            last_account_root_file.last_block_number
        )

        account_root_file = copy.deepcopy(last_account_root_file)
        account_root_file_accounts = account_root_file.account_states

        block = None
        for block in self.iter_blocks_from(account_root_file.get_next_block_number()):  # type: ignore
            if last_block_number is not None and block.message.block_number > last_block_number:
                logger.debug('Traversed all blocks of interest')
                break

            logger.debug('Traversing block number %s', block.message.block_number)
            for account_number, account_balance in block.message.updated_account_states.items():
                logger.debug('Found %s account balance: %s', account_number, account_balance)
                arf_balance = account_root_file_accounts.get(account_number)
                if arf_balance is None:
                    logger.debug('Account %s is met for the first time (empty lock is expected)', account_number)
                    assert account_balance.balance_lock is None
                    arf_balance = AccountState(balance=account_balance.balance, balance_lock=account_number)
                    account_root_file_accounts[account_number] = arf_balance
                else:
                    arf_balance.balance = account_balance.balance
                    lock = account_balance.balance_lock
                    if lock:
                        arf_balance.balance_lock = lock

        if block is not None:
            account_root_file.last_block_number = block.message.block_number
            account_root_file.last_block_identifier = block.message.block_identifier
            account_root_file.last_block_timestamp = block.message.timestamp
            account_root_file.next_block_identifier = block.message_hash

        return account_root_file
