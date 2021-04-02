import copy
import logging
from typing import Generator, Optional

from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block

from .base import BlockchainBase

logger = logging.getLogger(__name__)


class MemoryBlockchain(BlockchainBase):
    """
    A blockchain implementation primarily for use in unittesting and being used as an example implementation
    """

    def __init__(self, *, base_account_root_file):
        self.account_root_files: list[AccountRootFile] = []
        self.blocks: list[Block] = []

        super().__init__(base_account_root_file=base_account_root_file)

    # Account root files related implemented methods
    def add_account_root_file(self, account_root_file: AccountRootFile):
        is_initial = False if self.account_root_files else account_root_file.is_initial()
        account_root_file.validate(is_initial=is_initial)

        self.account_root_files.append(account_root_file)

    def get_first_account_root_file(self) -> Optional[AccountRootFile]:
        account_root_files = self.account_root_files
        if account_root_files:
            return account_root_files[0]

        return None

    def get_last_account_root_file(self) -> Optional[AccountRootFile]:
        account_root_files = self.account_root_files
        if account_root_files:
            return account_root_files[-1]

        return None

    def get_account_root_file_count(self) -> int:
        return len(self.account_root_files)

    def iter_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        yield from self.account_root_files

    def iter_account_root_files_reversed(self) -> Generator[AccountRootFile, None, None]:
        yield from reversed(self.account_root_files)

    # Blocks related implemented methods
    def persist_block(self, block: Block):
        self.blocks.append(copy.deepcopy(block))

    def get_last_block(self) -> Optional[Block]:
        blocks = self.blocks
        if blocks:
            return blocks[-1]

        return None

    def get_first_block(self) -> Optional[Block]:
        blocks = self.blocks
        if blocks:
            return blocks[0]

        return None

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
