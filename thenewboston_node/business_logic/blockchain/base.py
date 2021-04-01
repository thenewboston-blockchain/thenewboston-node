import copy
import logging
from itertools import chain, dropwhile, islice
from typing import Generator, Iterable, Optional, Type, TypeVar, cast

from django.conf import settings

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.account_balance import AccountBalance, BlockAccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.core.logging import validates, verbose_timeit_method
from thenewboston_node.core.utils.importing import import_from_string

from ..models.block import Block

T = TypeVar('T', bound='BlockchainBase')

logger = logging.getLogger(__name__)
validation_logger = logging.getLogger(__name__ + '.validation_logger')


class BlockchainBase:

    _instance = None

    def __init__(self, *, initial_account_root_file):
        self.add_account_root_file(initial_account_root_file)

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

    # Account root files related abstract methods
    def add_account_root_file(self, account_root_file: AccountRootFile):
        raise NotImplementedError('Must be implemented in a child class')

    def get_first_account_root_file(self) -> Optional[AccountRootFile]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_last_account_root_file(self) -> Optional[AccountRootFile]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_account_root_file_count(self) -> int:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_account_root_files_reversed(self) -> Generator[AccountRootFile, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    # Blocks related abstract methods
    def persist_block(self, block: Block):
        raise NotImplementedError('Must be implemented in a child class')

    def get_last_block(self) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_first_block(self) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_by_number(self, block_number: int) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_by_identifier(self, block_number: int) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_count(self) -> int:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_blocks(self) -> Generator[Block, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_blocks_from(self, block_number: int) -> Generator[Block, None, None]:
        # TODO(dmu) HIGH: Implement higher performance iter_blocks_from() in child classes
        logger.warning(
            'Low performance iter_blocks_from() implementation is being used (override with better '
            'performance implementation)'
        )
        yield from dropwhile(lambda _block: _block.message.block_number < block_number, self.iter_blocks())

    def iter_blocks_reversed(self) -> Generator[Block, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    # Base methods
    def add_block(self, block: Block):
        block_number = block.message.block_number
        if block_number != self.get_next_block_number():
            raise ValidationError('Block number must be equal to next block number (== head block number + 1)')

        block.validate(self)
        # TODO(dmu) HIGH: Validate block_identifier

        self.persist_block(block)

    def validate_before_block_number(self, before_block_number: Optional[int]) -> int:
        next_block_number = self.get_next_block_number()
        if before_block_number is None:
            return next_block_number
        elif before_block_number < 0:
            raise ValueError('block_number must be greater or equal to 0')
        elif before_block_number > next_block_number:
            raise ValueError('block_number must be less or equal to next block number')

        return before_block_number

    def get_balance_value(self, account: str, before_block_number: Optional[int] = None) -> Optional[int]:
        """
        Return balance value before `before_block_number` is applied. If `before_block_number` is not specified it
        defaults to the next block number.
        """
        block_number = self.validate_before_block_number(before_block_number) - 1
        balance_value = self._get_balance_value_from_block(account, block_number)
        if balance_value is None:
            balance_value = self._get_balance_value_from_account_root_file(account, block_number)

        return balance_value

    @verbose_timeit_method()
    def get_balance_lock(self, account: str, before_block_number: Optional[int] = None) -> str:
        """
        Return balance lock before `before_block_number` is applied. If `before_block_number` is not specified it
        defaults to the next block number.
        """
        block_number = self.validate_before_block_number(before_block_number) - 1
        lock = self._get_balance_lock_from_block(account, block_number)
        if lock:
            return lock

        lock = self._get_balance_lock_from_account_root_file(account, block_number)
        return account if lock is None else lock

    @verbose_timeit_method()
    def _get_balance_lock_from_block(self, account: str, block_number: Optional[int] = None) -> Optional[str]:
        balance = self._get_balance_from_block(account, block_number, must_have_lock=True)
        return None if balance is None else balance.lock

    def _get_balance_lock_from_account_root_file(self,
                                                 account: str,
                                                 block_number: Optional[int] = None) -> Optional[str]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.lock

    def _get_balance_value_from_block(self, account: str, block_number: Optional[int] = None) -> Optional[int]:
        balance = self._get_balance_from_block(account, block_number)
        return None if balance is None else balance.value

    @verbose_timeit_method()
    def _get_balance_from_block(self,
                                account: str,
                                block_number: Optional[int] = None,
                                must_have_lock: bool = False) -> Optional[BlockAccountBalance]:
        for block in self.get_blocks_until_account_root_file(block_number):
            balance = block.message.get_balance(account)
            if balance is not None:
                if must_have_lock:
                    lock = balance.lock
                    if lock:
                        return balance
                else:
                    return balance

        return None

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
        assert (
            from_block_number is None or account_root_file_block_number is None or
            account_root_file_block_number <= from_block_number
        )

        current_head_block = self.get_last_block()
        assert current_head_block
        current_head_block_number = current_head_block.message.block_number
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
        logger.debug('Returning blocks head offset from %s to %s', -start, -stop)
        # TODO(dmu) HIGH: Consider performance optimizations for islice(self.iter_blocks_reversed(), start, stop, 1)
        block = None
        for block in islice(self.iter_blocks_reversed(), start, stop, 1):
            assert (
                account_root_file_block_number is None or account_root_file_block_number < block.message.block_number
            )

            logger.debug('Returning block: %s', block)
            yield block

        # Assert we traversed all blocks up to the account root file
        if block:
            block_number = block.message.block_number
            assert (
                account_root_file_block_number is None and block_number == 0 or
                account_root_file_block_number is not None and block_number == account_root_file_block_number + 1
            )

    def _get_balance_value_from_account_root_file(self,
                                                  account: str,
                                                  block_number: Optional[int] = None) -> Optional[int]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.value

    def _get_balance_from_account_root_file(self,
                                            account: str,
                                            block_number: Optional[int] = None) -> Optional[AccountBalance]:
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
            logger.warning('Could not find account root file that excludes block number %s')
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
            for account_number, account_balance in block.message.updated_balances.items():
                logger.debug('Found %s account balance: %s', account_number, account_balance)
                arf_balance = account_root_file_accounts.get(account_number)
                if arf_balance is None:
                    logger.debug('Account %s is met for the first time (empty lock is expected)', account_number)
                    assert account_balance.lock is None
                    arf_balance = AccountBalance(value=account_balance.value, lock=account_number)
                    account_root_file_accounts[account_number] = arf_balance
                else:
                    arf_balance.value = account_balance.value
                    lock = account_balance.lock
                    if lock:
                        arf_balance.lock = lock

        if block is not None:
            account_root_file.last_block_number = block.message.block_number
            account_root_file.last_block_identifier = block.message.block_identifier
            account_root_file.next_block_identifier = block.message_hash

        return account_root_file

    def validate(self, block_offset: int = None, block_limit: int = None, is_partial_allowed: bool = True):
        validation_logger.debug('===> Validating the BLOCKCHAIN')
        if is_partial_allowed:
            raise NotImplementedError('Partial blockchains are not supported yet')

        if block_offset is not None or block_limit is not None:
            raise NotImplementedError('Block limit/offset is not fully supported yet')

        self.validate_account_root_files()
        self.validate_blocks(offset=block_offset, limit=block_limit)
        validation_logger.debug('===> The BLOCKCHAIN is valid')

    @validates('account root files', logger=validation_logger, is_plural_target=True)
    def validate_account_root_files(self):
        account_root_files_iter = self.iter_account_root_files()
        with validates('number of account root files (at least one)', logger=validation_logger):
            try:
                first_account_root_file = next(account_root_files_iter)
            except StopIteration:
                raise ValidationError('Blockchain must contain at least one account root file')

        is_initial = first_account_root_file.is_initial()
        for counter, account_root_file in enumerate(chain((first_account_root_file,), account_root_files_iter)):
            with validates(f'account root file number {counter}', logger=validation_logger):
                self.validate_account_root_file(account_root_file=account_root_file, is_initial=is_initial)

            is_initial = False  # only first iteration can be with initial

    @validates('account root file (last_block_number={account_root_file.last_block_number})')
    def validate_account_root_file(self, *, account_root_file, is_initial=False):
        account_root_file.validate(is_initial=is_initial)
        if is_initial:
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
        for account_number, account_balance in generated_account_root_file.accounts.items():
            with validates(f'account {account_number} existence'):
                actual_account_balance = actual_accounts.get(account_number)
                if actual_account_balance is None:
                    raise ValidationError(f'Could not find {account_number} account in the account root file')

            with validates(f'account {account_number} balance value'):
                expect_value = account_balance.value
                actual_value = actual_account_balance.value
                if actual_value != expect_value:
                    raise ValidationError(
                        f'Expected {expect_value} balance value, '
                        f'but got {actual_value} balance value for account {account_number}'
                    )

            with validates(f'account {account_number} balance lock'):
                expect_lock = account_balance.lock
                actual_lock = actual_account_balance.lock
                if actual_lock != expect_lock:
                    raise ValidationError(
                        f'Expected {expect_lock} balance lock, but got {actual_lock} balance '
                        f'lock for account {account_number}'
                    )

    def validate_blocks(self, offset: Optional[int] = None, limit: Optional[int] = None):
        """
        Validate blocks persisted in the blockchain. Some blockchain level validations may overlap with
        block level validations. We consider it OK since it is better to double check something rather
        than miss something. We may reconsider this overlap in favor of validation performance.
        """

        # TODO(dmu) CRITICAL: Validate that the first block is based on an existing root account file

        validation_logger.debug('Validating the blockchain blocks')
        blocks_iter = cast(Iterable[Block], self.iter_blocks())
        if offset is not None or limit is not None:
            start = offset or 0
            # TODO(dmu) HIGH: Consider performance improvements when slicing
            if limit is None:
                blocks_iter = islice(blocks_iter, start)
            else:
                blocks_iter = islice(blocks_iter, start, start + limit)

        try:
            first_block = next(blocks_iter)  # type: ignore
        except StopIteration:
            return

        self.validate_first_block(first_block)
        expected_block_number = first_block.message.block_number + 1
        expected_block_identifier = first_block.message_hash

        for block in blocks_iter:
            self.validate_block(block, expected_block_number, expected_block_identifier)
            expected_block_number += 1
            expected_block_identifier = block.message_hash
        validation_logger.debug('The blockchain blocks are valid')

    def validate_first_block(self, first_block: Block):
        validation_logger.debug('Validating the first block of the blockchain')
        account_root_file = self.get_first_account_root_file()
        assert account_root_file
        # TODO(dmu) CRITICAL: Support partial blockchains
        assert account_root_file.is_initial()

        self.validate_block(
            first_block,
            expected_block_number=account_root_file.get_next_block_number(),
            expected_block_identifier=account_root_file.get_next_block_identifier(),
        )
        validation_logger.debug('The first block of the blockchain is valid')

    def validate_block(self, block: Block, expected_block_number: int, expected_block_identifier: str):
        actual_block_number = block.message.block_number
        actual_block_identifier = block.message.block_identifier

        validation_logger.debug(
            'Validating block number %s (identifier: %s) on blockchain level', actual_block_number,
            actual_block_identifier
        )

        if actual_block_number != expected_block_number:
            raise ValidationError(f'Expected block number {expected_block_number} but got {actual_block_number}')
        validation_logger.debug('Block number is %s (as expected)', expected_block_number)

        if actual_block_identifier != expected_block_identifier:
            raise ValidationError(
                f'Expected block identifier {expected_block_identifier} but got {actual_block_identifier}'
            )
        validation_logger.debug('Block identifier is %s (as expected)', expected_block_identifier)

        block.validate(self)
        validation_logger.debug(
            'The block number %s (identifier: %s) is valid on blockchain level', actual_block_number,
            actual_block_identifier
        )
