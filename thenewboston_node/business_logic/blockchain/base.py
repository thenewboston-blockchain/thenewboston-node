import copy
import logging
from itertools import islice
from typing import Generator, Iterable, Optional, Type, TypeVar, cast

from django.conf import settings

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
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
        block.validate(self)
        # TODO(dmu) HIGH: Validate block_number is head_block_number + 1
        # TODO(dmu) HIGH: Validate block_identifier

        self.persist_block(block)

    def persist_block(self, block: Block):
        raise NotImplementedError('Must be implemented in a child class')

    def get_balance_value(self, account: str, on_block_number: Optional[int] = None) -> Optional[int]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_balance_lock(self, account: str, on_block_number: Optional[int] = None) -> str:
        raise NotImplementedError('Must be implemented in a child class')

    def get_head_block(self) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_by_number(self, block_number: int) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_block_by_identifier(self, block_number: int) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def iter_blocks(self) -> Generator[Block, None, None]:
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

    def get_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_account_root_files_reversed(self) -> Generator[AccountRootFile, None, None]:
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
            for account_root_file in self.get_account_root_files_reversed():
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
        for account_root_file in islice(self.get_account_root_files(), 1):
            # TODO(dmu) CRITICAL: Validate last_block_number and last_block_identifiers point to correct blocks
            account_root_file.validate()

    def validate_blocks(self, offset: Optional[int] = None, limit: Optional[int] = None):
        # Validations to be implemented:
        # 1. Block numbers are sequential
        # 2. Block identifiers equal to previous block message hash
        # 3. Each individual block is valid
        # 4. First block identifier equals to initial account root file hash

        blocks_iter = cast(Iterable[Block], self.iter_blocks())
        if offset is not None or limit is not None:
            start = offset or 0
            if limit is None:
                blocks_iter = islice(blocks_iter, start)
            else:
                blocks_iter = islice(blocks_iter, start, start + limit)

        for block in blocks_iter:
            block.validate(self)
