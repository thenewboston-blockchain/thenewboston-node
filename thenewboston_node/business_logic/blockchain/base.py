import copy
import logging
import warnings
from itertools import chain, dropwhile, islice
from typing import Generator, Iterable, Optional, Type, TypeVar, cast

from django.conf import settings

from more_itertools import always_reversible, ilen

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import AccountStateUpdate, CoinTransferSignedRequest
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.core.logging import timeit, timeit_method, validates
from thenewboston_node.core.utils.importing import import_from_string

from ..models.block import Block

T = TypeVar('T', bound='BlockchainBase')

logger = logging.getLogger(__name__)


class BlockchainBase:

    _instance = None

    def __init__(self, arf_creation_period_in_blocks=None):
        self.arf_creation_period_in_blocks = arf_creation_period_in_blocks

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            blockchain_settings = settings.BLOCKCHAIN
            class_ = import_from_string(blockchain_settings['class'])
            instance = class_(**(blockchain_settings.get('kwargs') or {}))
            cls._instance = instance

        return instance

    @classmethod
    def clear_instance_cache(cls):
        cls._instance = None

    # * Abstract methods
    # ** Account root files related abstract methods
    def persist_account_root_file(self, account_root_file: AccountRootFile):
        raise NotImplementedError('Must be implemented in a child class')

    def iter_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    # ** Blocks related abstract methods
    def persist_block(self, block: Block):
        raise NotImplementedError('Must be implemented in a child class')

    def iter_blocks(self) -> Generator[Block, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    # * Override recommended methods
    # ** Account root files related override recommended methods
    def get_account_root_file_count(self) -> int:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn('Using low performance implementation of get_account_root_file_count() method (override it)')
        return ilen(self.iter_account_root_files())

    def iter_account_root_files_reversed(self) -> Generator[AccountRootFile, None, None]:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn(
            'Using low performance implementation of iter_account_root_files_reversed() method (override it)'
        )
        yield from always_reversible(self.iter_account_root_files())

    # ** Blocks related override recommended methods
    def get_block_count(self) -> int:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn('Using low performance implementation of get_block_count() method (override it)')
        return ilen(self.iter_blocks())

    def iter_blocks_from(self, block_number: int) -> Generator[Block, None, None]:
        # TODO(dmu) HIGH: Implement higher performance iter_blocks_from() in child classes
        warnings.warn(
            'Low performance iter_blocks_from() implementation is being used (override with better '
            'performance implementation)'
        )
        yield from dropwhile(lambda _block: _block.message.block_number < block_number, self.iter_blocks())

    def iter_blocks_reversed(self) -> Generator[Block, None, None]:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn('Using low performance implementation of iter_blocks_reversed() method (override it)')
        yield from always_reversible(self.iter_blocks())

    def get_block_by_number(self, block_number: int) -> Optional[Block]:
        # Highly recommended to override this method in the particular implementation of the blockchain for
        # performance reasons
        warnings.warn('Using low performance implementation of get_block_by_number() method (override it)')
        for block in self.iter_blocks():
            current_block_number = block.message.block_number
            if current_block_number == block_number:
                return block
            elif current_block_number > block_number:
                break

        return None

    # * Base methods
    # ** Account root files related base methods
    def add_account_root_file(self, account_root_file: AccountRootFile):
        account_root_file.validate(is_initial=account_root_file.is_initial())
        self.persist_account_root_file(account_root_file)

    def get_first_account_root_file(self) -> Optional[AccountRootFile]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.iter_account_root_files())
        except StopIteration:
            return None

    def get_last_account_root_file(self) -> Optional[AccountRootFile]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.iter_account_root_files_reversed())
        except StopIteration:
            return None

    # ** Blocks related base methods
    @timeit_method(level=logging.INFO)
    def add_block(self, block: Block, validate=True):
        block_number = block.message.block_number
        if validate:
            if block_number != self.get_next_block_number():
                raise ValidationError('Block number must be equal to next block number (== head block number + 1)')

            block.validate(self)

        # TODO(dmu) HIGH: Validate block_identifier

        self.persist_block(block)

        period = self.arf_creation_period_in_blocks
        if period is not None and (block_number + 1) % period == 0:
            self.make_account_root_file()

    def get_first_block(self) -> Optional[Block]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.iter_blocks())
        except StopIteration:
            return None

    def get_last_block(self) -> Optional[Block]:
        # Override this method if a particular blockchain implementation can provide a high performance
        try:
            return next(self.iter_blocks_reversed())
        except StopIteration:
            return None

    # Not sorted (yet) methods
    def iter_known_accounts(self):
        known_accounts = set()
        for block in self.get_blocks_until_account_root_file():
            block_accounts = set(block.message.account_state_updates.keys())
            new_accounts = block_accounts - known_accounts
            known_accounts |= new_accounts
            for new_account in new_accounts:
                yield new_account

        last_account_root_file = self.get_first_account_root_file()
        account_root_file_accounts = last_account_root_file.accounts.keys()
        new_accounts = account_root_file_accounts - known_accounts
        known_accounts |= new_accounts
        for new_account in new_accounts:
            yield new_account

    @timeit_method(level=logging.INFO)
    def add_block_from_transfer_request(self, transfer_request: CoinTransferSignedRequest, validate=True):
        block = Block.from_transfer_request(self, transfer_request)
        self.add_block(block, validate=validate)

    def validate_before_block_number(self, before_block_number: Optional[int]) -> int:
        next_block_number = self.get_next_block_number()
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
        balance = self._get_balance_from_block(account, block_number, must_have_lock=True)
        return None if balance is None else balance.balance_lock

    def _get_account_lock_from_account_root_file(self,
                                                 account: str,
                                                 block_number: Optional[int] = None) -> Optional[str]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.balance_lock

    def _get_account_balance_from_block(self, account: str, block_number: Optional[int] = None) -> Optional[int]:
        balance = self._get_balance_from_block(account, block_number)
        return None if balance is None else balance.balance

    @timeit_method()
    def _get_balance_from_block(self,
                                account: str,
                                block_number: Optional[int] = None,
                                must_have_lock: bool = False) -> Optional[AccountStateUpdate]:
        for block in self.get_blocks_until_account_root_file(block_number):
            balance = block.message.get_balance(account)
            if balance is not None:
                if must_have_lock:
                    lock = balance.balance_lock
                    if lock:
                        return balance
                else:
                    return balance

        return None

    @timeit(is_method=True, verbose_args=True)
    def get_blocks_until_account_root_file(self, from_block_number: Optional[int] = None):
        """
        Return generator of block traversing from `from_block_number` block (or head block if not specified)
        to the block in included in the closest account root file (exclusive: the account root file block is not
        traversed).
        """
        if from_block_number is not None and from_block_number < 0:
            logger.debug('No blocks to return: from_block_number (== %s) is less than 0', from_block_number)
            return

        block_count = self.get_block_count()
        assert block_count >= 0
        if block_count == 0:
            logger.debug('No blocks to return: blockchain does not contain blocks')
            return

        excludes_block_number = None if from_block_number is None else (from_block_number + 1)
        account_root_file = self.get_closest_account_root_file(excludes_block_number)
        if account_root_file is None:
            logger.warning('Could not find account root file excluding from_block_number: %s', from_block_number)
            return

        account_root_file_block_number = account_root_file.last_block_number
        logger.debug('Closest account root file last block number is %s', account_root_file_block_number)
        assert (
            from_block_number is None or account_root_file_block_number is None or
            account_root_file_block_number <= from_block_number
        )

        current_head_block = self.get_last_block()
        assert current_head_block
        current_head_block_number = current_head_block.message.block_number
        logger.debug('Head block number is %s', current_head_block_number)

        if from_block_number is None or from_block_number > current_head_block_number:
            offset = 0
        else:
            offset = current_head_block_number - from_block_number

        if account_root_file_block_number is None:
            blocks_to_return = block_count - offset
        else:
            blocks_to_return = current_head_block_number - account_root_file_block_number - offset

        start = offset
        stop = offset + blocks_to_return
        logger.debug(
            'Returning blocks head offset from %s to %s (%s block(s) to return)', -start, -stop, blocks_to_return
        )
        # TODO(dmu) HIGH: Consider performance optimizations for islice(self.iter_blocks_reversed(), start, stop, 1)
        block = None
        for block in islice(self.iter_blocks_reversed(), start, stop, 1):
            block_number = block.message.block_number
            assert account_root_file_block_number is None or account_root_file_block_number < block_number
            logger.debug('Returning block number: %s', block_number)
            yield block

        logger.debug('All blocks have been iterated over')
        # Assert we traversed all blocks up to the account root file
        if block:
            block_number = block.message.block_number
            if account_root_file_block_number is None:
                assert block_number == 0
            else:
                assert block_number == account_root_file_block_number + 1

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
        return account_root_file.get_balance(account)

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

        block = self.get_block_by_number(prev_block_number)
        assert block is not None
        return block.message_hash

    def get_next_block_identifier(self) -> str:
        block_identifier = self.get_expected_block_identifier(self.get_next_block_number())
        assert block_identifier
        return block_identifier

    def get_next_block_number(self) -> int:
        last_block = self.get_last_block()
        if last_block:
            return last_block.message.block_number + 1

        account_root_file = self.get_closest_account_root_file()
        assert account_root_file
        return account_root_file.get_next_block_number()

    def get_closest_account_root_file(self, excludes_block_number: Optional[int] = None) -> Optional[AccountRootFile]:
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
            account_root_file = self.get_last_account_root_file()
        elif excludes_block_number == -1:
            logger.debug('excludes_block_number == -1: initial account root file is requested (not just first)')
            first_account_root_file = self.get_first_account_root_file()
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
            for account_root_file in self.iter_account_root_files_reversed():
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

    def make_account_root_file(self):
        last_block = self.get_last_block()
        if last_block is None:
            logger.warning('Blocks are not found: making account root file does not make sense')
            return None

        last_account_root_file = self.get_last_account_root_file()
        assert last_account_root_file is not None

        if not last_account_root_file.is_initial():
            assert last_account_root_file.last_block_number is not None
            if last_block.message.block_number <= last_account_root_file.last_block_number:
                logger.debug('The last block is already included in the last account root file')
                return None

        account_root_file = self.generate_account_root_file()
        self.add_account_root_file(account_root_file)

    def generate_account_root_file(self, last_block_number: Optional[int] = None) -> AccountRootFile:
        last_account_root_file = self.get_closest_account_root_file(last_block_number)
        assert last_account_root_file is not None
        logger.debug(
            'Generating account root file based on account root file with last_block_number=%s',
            last_account_root_file.last_block_number
        )

        account_root_file = copy.deepcopy(last_account_root_file)
        account_root_file_accounts = account_root_file.accounts

        block = None
        for block in self.iter_blocks_from(account_root_file.get_next_block_number()):
            if last_block_number is not None and block.message.block_number > last_block_number:
                logger.debug('Traversed all blocks of interest')
                break

            logger.debug('Traversing block number %s', block.message.block_number)
            for account_number, account_balance in block.message.account_state_updates.items():
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

    # Validation methods
    @validates('BLOCKCHAIN')
    def validate(self, is_partial_allowed: bool = True):
        self.validate_account_root_files(is_partial_allowed=is_partial_allowed)
        self.validate_blocks()

    @validates('account root files', is_plural_target=True)
    def validate_account_root_files(self, is_partial_allowed: bool = True):
        account_root_files_iter = self.iter_account_root_files()
        with validates('number of account root files (at least one)'):
            try:
                first_account_root_file = next(account_root_files_iter)
            except StopIteration:
                raise ValidationError('Blockchain must contain at least one account root file')

        is_initial = first_account_root_file.is_initial()
        if not is_partial_allowed and not is_initial:
            raise ValidationError('Blockchain must start with initial account root file')

        is_first = True
        for counter, account_root_file in enumerate(chain((first_account_root_file,), account_root_files_iter)):
            with validates(f'account root file number {counter}'):
                self.validate_account_root_file(
                    account_root_file=account_root_file, is_initial=is_initial, is_first=is_first
                )

            is_initial = False  # only first iteration can be with initial
            is_first = False

    @validates('account root file (last_block_number={account_root_file.last_block_number})')
    def validate_account_root_file(self, *, account_root_file, is_initial=False, is_first=False):
        account_root_file.validate(is_initial=is_initial)
        if is_initial:
            return

        if is_first:
            logger.debug('First account root file is not a subject of further validations')
            return

        self.validate_account_root_file_balances(account_root_file=account_root_file)

        first_block = self.get_first_block()
        if not first_block:
            return

        if first_block.message.block_number > account_root_file.last_block_number:
            logger.debug('First block is after the account root file')
            if first_block.message.block_number > account_root_file.last_block_number + 1:
                logger.warning('Unnecessary old account root file detected')

            return

        # If account root file is after first known block then we can validate its attributes
        account_root_file_last_block = self.get_block_by_number(account_root_file.last_block_number)
        with validates('account root file last_block_number'):
            if account_root_file_last_block is None:
                raise ValidationError('Account root file last_block_number points to non-existing block')

        with validates('account root file last_block_identifier'):
            if account_root_file_last_block.message.block_identifier != account_root_file.last_block_identifier:
                raise ValidationError('Account root file last_block_number does not match last_block_identifier')

        with validates('account root file next_block_identifier'):
            if account_root_file_last_block.message_hash != account_root_file.next_block_identifier:
                raise ValidationError(
                    'Account root file next_block_identifier does not match last_block_number message hash'
                )

    @validates(
        'account root file balances (last_block_number={account_root_file.last_block_number})', is_plural_target=True
    )
    def validate_account_root_file_balances(self, *, account_root_file):
        generated_account_root_file = self.generate_account_root_file(account_root_file.last_block_number)
        with validates('number of account root file balances'):
            expected_accounts_count = len(generated_account_root_file.accounts)
            actual_accounts_count = len(account_root_file.accounts)
            if expected_accounts_count != actual_accounts_count:
                raise ValidationError(
                    f'Expected {expected_accounts_count} accounts, '
                    f'but got {actual_accounts_count} in the account root file'
                )

        actual_accounts = account_root_file.accounts
        for account_number, account_state in generated_account_root_file.accounts.items():
            with validates(f'account {account_number} existence'):
                actual_account_state = actual_accounts.get(account_number)
                if actual_account_state is None:
                    raise ValidationError(f'Could not find {account_number} account in the account root file')

            with validates(f'account {account_number} balance value'):
                expect_balance = account_state.balance
                actual_state = actual_account_state.balance
                if actual_state != expect_balance:
                    raise ValidationError(
                        f'Expected {expect_balance} balance value, '
                        f'but got {actual_state} balance value for account {account_number}'
                    )

            with validates(f'account {account_number} balance lock'):
                expect_lock = account_state.balance_lock
                actual_lock = actual_account_state.balance_lock
                if actual_lock != expect_lock:
                    raise ValidationError(
                        f'Expected {expect_lock} balance lock, but got {actual_lock} balance '
                        f'lock for account {account_number}'
                    )

    @validates('blockchain blocks (offset={offset}, limit={limit})', is_plural_target=True, use_format_map=True)
    def validate_blocks(self, *, offset: int = 0, limit: Optional[int] = None):
        """
        Validate blocks persisted in the blockchain. Some blockchain level validations may overlap with
        block level validations. We consider it OK since it is better to double check something rather
        than miss something. We may reconsider this overlap in favor of validation performance.
        """
        assert offset >= 0

        blocks_iter = cast(Iterable[Block], self.iter_blocks())
        if offset > 0 or limit is not None:
            # TODO(dmu) HIGH: Consider performance improvements when slicing
            if limit is None:
                blocks_iter = islice(blocks_iter, offset)
            else:
                blocks_iter = islice(blocks_iter, offset, offset + limit)

        try:
            first_block = next(blocks_iter)  # type: ignore
        except StopIteration:
            return

        first_account_root_file = self.get_first_account_root_file()
        if first_account_root_file is None:
            raise ValidationError('Account root file prior to first block is not found')

        first_block_number = first_block.message.block_number
        if offset == 0:
            with validates('basing on an account root file'):

                if first_account_root_file.get_next_block_number() != first_block_number:
                    raise ValidationError('First block number does not match base account root file last block number')

                if first_account_root_file.get_next_block_identifier() != first_block.message.block_identifier:
                    raise ValidationError(
                        'First block identifier does not match base account root file last block identifier'
                    )

            expected_block_identifier = first_account_root_file.get_next_block_identifier()
        else:
            prev_block = self.get_block_by_number(first_block_number - 1)
            if prev_block is None:
                raise ValidationError(f'Previous block for block number {first_block_number} is not found')

            assert prev_block.message_hash
            expected_block_identifier = prev_block.message_hash

        expected_block_number = first_account_root_file.get_next_block_number() + offset
        for block in chain((first_block,), blocks_iter):
            block.validate(self)

            assert block.message

            self.validate_block(
                block=block,
                expected_block_number=expected_block_number,
                expected_block_identifier=expected_block_identifier
            )
            expected_block_number += 1
            expected_block_identifier = block.message_hash

    @validates(
        'block number {block.message.block_number} (identifier: block.message.block_identifier) '
        'on blockchain level'
    )
    def validate_block(self, *, block: Block, expected_block_number: int, expected_block_identifier: str):
        actual_block_number = block.message.block_number
        actual_block_identifier = block.message.block_identifier

        if actual_block_number != expected_block_number:
            raise ValidationError(f'Expected block number {expected_block_number} but got {actual_block_number}')

        if actual_block_identifier != expected_block_identifier:
            raise ValidationError(
                f'Expected block identifier {expected_block_identifier} but got {actual_block_identifier}'
            )
