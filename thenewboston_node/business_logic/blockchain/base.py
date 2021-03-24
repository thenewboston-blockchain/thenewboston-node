import copy
import logging
from itertools import islice
from typing import Generator, Iterable, Optional, Type, TypeVar, cast

from django.conf import settings

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.account_balance import AccountBalance, BlockAccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.core.logging import verbose_timeit_method
from thenewboston_node.core.utils.importing import import_from_string

from ..models.block import Block

T = TypeVar('T', bound='BlockchainBase')

logger = logging.getLogger(__name__)


class BlockchainBase:

    _instance = None

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

    def add_block(self, block: Block):
        block_number = block.message.block_number
        if block_number != self.get_next_block_number():
            raise ValidationError('Block number must be equal to next block number (== head block number + 1)')

        block.validate(self)
        # TODO(dmu) HIGH: Validate block_identifier

        self.persist_block(block)

    def persist_block(self, block: Block):
        raise NotImplementedError('Must be implemented in a child class')

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

        account_root_file = self.get_closest_account_root_file(from_block_number)
        if account_root_file is None:
            logger.warning('Could not find account root file excluding from_block_number: %s', from_block_number)
            return

        account_root_file_block_number = account_root_file.last_block_number
        assert (
            from_block_number is None or account_root_file_block_number is None or
            account_root_file_block_number <= from_block_number
        )

        current_head_block = self.get_head_block()
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
        for block in islice(self.iter_blocks_reversed(), start, stop, 1):
            assert (
                account_root_file_block_number is None or account_root_file_block_number < block.message.block_number
            )

            logger.debug('Returning block: %s', block)
            yield block

    def _get_balance_value_from_account_root_file(self,
                                                  account: str,
                                                  block_number: Optional[int] = None) -> Optional[int]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.value

    def _get_balance_from_account_root_file(self,
                                            account: str,
                                            block_number: Optional[int] = None) -> Optional[AccountBalance]:
        account_root_file = self.get_closest_account_root_file(block_number)
        assert account_root_file
        return account_root_file.get_balance(account)

    def get_head_block(self) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_by_number(self, block_number: int) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_by_identifier(self, block_number: int) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_blocks(self) -> Generator[Block, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_blocks_reversed(self) -> Generator[Block, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_count(self) -> int:
        raise NotImplementedError('Must be implemented in a child class')

    def get_expected_block_identifier(self, block_number: int) -> Optional[str]:
        """
        Return expected block identifier (take from previous block message hash or account root file)
        for the `block_number` (from 0 to head block number + 1 inclusive).

        To be used for validation of existing and generation of new blocks.
        """
        if block_number < 0:
            raise ValueError('block_number must be greater or equal to 0')

        prev_block_number = block_number - 1
        account_root_file = self.get_closest_account_root_file(prev_block_number)
        if account_root_file is None:
            logger.warning('Previous block number %s is beyond known account root files', prev_block_number)
            return None

        if block_number == 0:
            assert account_root_file.is_initial()
            return account_root_file.get_next_block_identifier()

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
        head_block = self.get_head_block()
        if head_block:
            return head_block.message.block_number + 1

        account_root_file = self.get_closest_account_root_file()
        assert account_root_file
        return account_root_file.get_next_block_number()

    def get_last_account_root_file(self) -> Optional[AccountRootFile]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_first_account_root_file(self) -> Optional[AccountRootFile]:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_account_root_files_reversed(self) -> Generator[AccountRootFile, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

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
            # We need just the last ARF (partial or complete blockchain is expected)
            account_root_file = self.get_last_account_root_file()
        elif excludes_block_number == -1:
            # We need the initial (not just first though) ARF (complete blockchain is expected)
            first_account_root_file = self.get_first_account_root_file()
            if first_account_root_file and first_account_root_file.is_initial():
                # We do have initial ARF -> complete blockchain
                account_root_file = first_account_root_file
            else:
                # We do not have initial ARF -> partial blockchain (unexpectedly)
                account_root_file = None
        else:
            # We need an intermediate ARF (partial or complete blockchain is expected)
            for account_root_file in self.iter_account_root_files_reversed():
                last_block_number = account_root_file.last_block_number
                if last_block_number is None or last_block_number <= excludes_block_number:
                    # We do have the intermediate ARF -> partial or complete blockchain
                    break
            else:
                # We do not have the intermediate ARF -> partial blockchain (unexpectedly short)
                account_root_file = None

        if account_root_file is None:
            logger.warning('Could not find account root file that excludes block number %s')
            return None

        return copy.deepcopy(account_root_file)

    def validate(self, block_offset: int = None, block_limit: int = None, is_partial_allowed: bool = True):
        if is_partial_allowed:
            raise NotImplementedError('Partial blockchains are not supported yet')

        if block_offset is not None or block_limit is not None:
            raise NotImplementedError('Block limit/offset is not fully supported yet')

        self.validate_account_root_files()
        self.validate_blocks(offset=block_offset, limit=block_limit)

    def validate_account_root_files(self):
        first_account_root_file = self.get_first_account_root_file()
        if not first_account_root_file:
            raise ValidationError('Blockchain must contain at least one account root file')

        first_account_root_file.validate(is_initial=first_account_root_file.is_initial())
        for account_root_file in islice(self.iter_account_root_files(), 1):
            # TODO(dmu) CRITICAL: Validate last_block_number and last_block_identifiers point to correct blocks
            account_root_file.validate()

    def validate_blocks(self, offset: Optional[int] = None, limit: Optional[int] = None):
        """
        Validate blocks persisted in the blockchain. Some blockchain level validations may overlap with
        block level validations. We consider it OK since it is better to double check something rather
        than miss something. We may reconsider this overlap in favor of validation performance.
        """

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

    def validate_first_block(self, first_block: Block):
        account_root_file = self.get_first_account_root_file()
        assert account_root_file
        # TODO(dmu) CRITICAL: Support partial blockchains
        assert account_root_file.is_initial()

        self.validate_block(
            first_block,
            expected_block_number=account_root_file.get_next_block_number(),
            expected_block_identifier=account_root_file.get_next_block_identifier(),
        )

    def validate_block(self, block: Block, expected_block_number: int, expected_block_identifier: str):
        actual_block_number = block.message.block_number
        if actual_block_number != expected_block_number:
            raise ValidationError(f'Expected block number {expected_block_number} but got {actual_block_number}')

        actual_block_identifier = block.message.block_identifier
        if actual_block_identifier != expected_block_identifier:
            raise ValidationError(
                f'Expected block identifier {expected_block_identifier} but got {actual_block_identifier}'
            )

        block.validate(self)
