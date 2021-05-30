import copy
import logging
from typing import Generator, Optional

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState

from .base import BlockchainBase

logger = logging.getLogger(__name__)


class MemoryBlockchain(BlockchainBase):
    """
    A blockchain implementation primarily for use in unittesting and being used as an example implementation
    """

    def __init__(
        self,
        *,
        account_root_files: list[BlockchainState] = None,
        blocks: Optional[list[Block]] = None,
        drop_intermediate_account_root_files=True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.blockchain_states: list[BlockchainState] = (
            copy.deepcopy(account_root_files) if account_root_files else []
        )
        self.blocks: list[Block] = copy.deepcopy(blocks) if blocks else []
        self.drop_intermediate_account_root_files = drop_intermediate_account_root_files

    # Account root files related implemented methods
    def persist_blockchain_state(self, account_root_file: BlockchainState):
        self.blockchain_states.append(account_root_file)

    def get_account_root_file_count(self) -> int:
        return len(self.blockchain_states)

    def iter_account_root_files(self) -> Generator[BlockchainState, None, None]:
        yield from self.blockchain_states

    def iter_account_root_files_reversed(self) -> Generator[BlockchainState, None, None]:
        yield from reversed(self.blockchain_states)

    def snapshot_blockchain_state(self):
        super().snapshot_blockchain_state()
        blockchain_states = self.blockchain_states
        if self.drop_intermediate_account_root_files and len(blockchain_states) > 2:
            self.blockchain_states = [blockchain_states[0], blockchain_states[-1]]

    # Blocks related implemented methods
    def persist_block(self, block: Block):
        self.blocks.append(copy.deepcopy(block))

    def get_block_by_number(self, block_number: int) -> Optional[Block]:
        if block_number < 0:
            raise ValueError('block_number must be greater or equal to 0')

        blocks = self.blocks
        if not blocks:
            return None

        head_block_number = blocks[-1].message.block_number
        if block_number > head_block_number:
            return None

        block_index = block_number - head_block_number - 1
        try:
            return blocks[block_index]
        except IndexError:
            assert blocks[0].message.block_number > block_number
            return None

    def get_block_count(self) -> int:
        return len(self.blocks)

    def iter_blocks(self) -> Generator[Block, None, None]:
        yield from self.blocks

    def iter_blocks_reversed(self) -> Generator[Block, None, None]:
        yield from reversed(self.blocks)

    def iter_blocks_from(self, block_number: int) -> Generator[Block, None, None]:
        # TODO(dmu) MEDIUM: This is questionable if this implementation is faster than base implementation
        #                   (because of extra memory use)
        blocks = self.blocks
        if blocks:
            first_block_number = blocks[0].message.block_number
            if first_block_number > block_number:
                logger.warning('Missing blocks from %s to %s', block_number, first_block_number - 1)
                start = 0
            else:
                start = block_number - first_block_number
        else:
            start = 0

        yield from self.blocks[start:]
