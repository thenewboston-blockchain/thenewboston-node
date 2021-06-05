import logging
import warnings
from itertools import dropwhile, islice
from typing import Generator, Optional

from more_itertools import always_reversible, ilen

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest
from thenewboston_node.core.logging import timeit, timeit_method

from ...models.block import Block

logger = logging.getLogger(__name__)


class BlocksMixin:

    def persist_block(self, block: Block):
        raise NotImplementedError('Must be implemented in a child class')

    def iter_blocks(self) -> Generator[Block, None, None]:
        raise NotImplementedError('Must be implemented in a child class')

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

        period = self.snapshot_period_in_blocks  # type: ignore
        if period is not None and (block_number + 1) % period == 0:
            self.snapshot_blockchain_state()  # type: ignore

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

    @timeit_method(level=logging.INFO)
    def add_block_from_signed_change_request(
        self, signed_change_request: CoinTransferSignedChangeRequest, validate=True
    ):
        block = Block.create_from_signed_change_request(self, signed_change_request)
        self.add_block(block, validate=validate)

    def get_next_block_identifier(self) -> str:
        block_identifier = self.get_expected_block_identifier(self.get_next_block_number())  # type: ignore
        assert block_identifier
        return block_identifier

    def get_next_block_number(self) -> int:
        last_block = self.get_last_block()
        if last_block:
            return last_block.message.block_number + 1

        account_root_file = self.get_closest_blockchain_state_snapshot()  # type: ignore
        assert account_root_file
        return account_root_file.get_next_block_number()

    def get_current_block_number(self):
        return self.get_next_block_number() - 1

    @timeit(is_method=True, verbose_args=True)
    def yield_blocks_till_snapshot(self, from_block_number: Optional[int] = None):
        """
        Return generator of block traversing from `from_block_number` block (or head block if not specified)
        to the block in included in the closest account root file (exclusive: the account root file block is not
        traversed).
        """
        if from_block_number is not None and from_block_number < 0:
            logger.debug('No blocks to return: from_block_number (== %s) is less than 0', from_block_number)
            return

        block_count = self.get_block_count()  # type: ignore
        assert block_count >= 0
        if block_count == 0:
            logger.debug('No blocks to return: blockchain does not contain blocks')
            return

        excludes_block_number = None if from_block_number is None else (from_block_number + 1)
        account_root_file = self.get_closest_blockchain_state_snapshot(excludes_block_number)  # type: ignore
        if account_root_file is None:
            logger.warning('Could not find account root file excluding from_block_number: %s', from_block_number)
            return

        account_root_file_block_number = account_root_file.last_block_number
        logger.debug('Closest account root file last block number is %s', account_root_file_block_number)
        assert (
            from_block_number is None or account_root_file_block_number is None or
            account_root_file_block_number <= from_block_number
        )

        current_head_block = self.get_last_block()  # type: ignore
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
        for block in islice(self.iter_blocks_reversed(), start, stop, 1):  # type: ignore
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