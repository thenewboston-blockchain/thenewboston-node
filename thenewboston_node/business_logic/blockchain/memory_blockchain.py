import copy
import logging
from itertools import islice
from typing import Generator, Optional

from thenewboston_node.business_logic.exceptions import MissingEarlierBlocksError
from thenewboston_node.business_logic.models.account_balance import AccountBalance, BlockAccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block

from .base import BlockchainBase

logger = logging.getLogger(__name__)


class MemoryBlockchain(BlockchainBase):
    """
    A blockchain implementation primarily for use in unittesting and being used as an example implementation
    """

    def __init__(self, *, initial_account_root_file):
        self.account_root_files: list[AccountRootFile] = [AccountRootFile.from_dict(initial_account_root_file)]

        self.blocks: list[Block] = []

    def iter_blocks(self) -> Generator[Block, None, None]:
        yield from self.blocks

    def persist_block(self, block: Block):
        self.blocks.append(copy.deepcopy(block))

    def get_head_block(self) -> Optional[Block]:
        blocks = self.blocks
        if blocks:
            return blocks[-1]

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
            raise MissingEarlierBlocksError()

    def get_blocks_until_account_root_file(self, start_block_number: Optional[int] = None):
        """
        Return generator of block traversing from `start_block_number` block (or head block if not specified)
        to the block in included in the closest account root file (exclusive: the account root file block is not
        traversed).
        """
        if start_block_number is not None and start_block_number < 0:
            return

        blocks = self.blocks
        if not blocks:
            return

        account_root_file = self.get_closest_account_root_file(start_block_number)
        if account_root_file is None:
            return

        account_root_file_block_number = account_root_file.last_block_number
        assert (
            start_block_number is None or account_root_file_block_number is None or
            account_root_file_block_number <= start_block_number
        )

        current_head_block = blocks[-1]
        current_head_block_number = current_head_block.message.block_number
        offset = 0 if start_block_number is None else (current_head_block_number - start_block_number)

        if account_root_file_block_number is None:
            blocks_to_return = len(blocks) - offset
        else:
            blocks_to_return = current_head_block_number - account_root_file_block_number - offset

        # TODO(dmu) HIGH: Consider performance optimizations for islice(reversed(blocks), offset, blocks_to_return, 1)
        for block in islice(reversed(blocks), offset, offset + blocks_to_return, 1):
            assert (
                account_root_file_block_number is None or account_root_file_block_number < block.message.block_number
            )

            yield block

    def _get_balance_value_from_block(self, account: str, on_block_number: Optional[int] = None) -> Optional[int]:
        balance = self._get_balance_from_block(account, on_block_number)
        return None if balance is None else balance.value

    def _get_balance_lock_from_block(self, account: str, on_block_number: Optional[int] = None) -> Optional[str]:
        balance = self._get_balance_from_block(account, on_block_number, must_have_lock=True)
        return None if balance is None else balance.lock

    def _get_balance_from_block(
        self,
        account: str,
        on_block_number: Optional[int] = None,
        must_have_lock: bool = False
    ) -> Optional[BlockAccountBalance]:
        for block in self.get_blocks_until_account_root_file(on_block_number):
            balance = block.message.get_balance(account)
            if balance is not None:
                if must_have_lock:
                    lock = balance.lock
                    if lock:
                        return balance
                else:
                    return balance

        return None

    def _get_balance_value_from_account_root_file(self,
                                                  account: str,
                                                  block_number: Optional[int] = None) -> Optional[int]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.value

    def _get_balance_lock_from_account_root_file(self,
                                                 account: str,
                                                 block_number: Optional[int] = None) -> Optional[str]:
        balance = self._get_balance_from_account_root_file(account, block_number)
        return None if balance is None else balance.lock

    def _get_balance_from_account_root_file(self,
                                            account: str,
                                            block_number: Optional[int] = None) -> Optional[AccountBalance]:
        account_root_file = self.get_closest_account_root_file(block_number)
        assert account_root_file
        return account_root_file.get_balance(account)

    def get_balance_value(self, account: str, on_block_number: Optional[int] = None) -> Optional[int]:
        """
        Returns account balance for the specified account. If block_number is specified then
        the account balance for that block is returned (after the block_number block is applied)
        otherwise the current (head block) balance is returned. If block_number is equal to -1 then
        account balance before 0 block is returned.
        """
        if on_block_number is not None and on_block_number < -1:
            raise ValueError('block_number must be greater or equal to -1')

        balance_value = self._get_balance_value_from_block(account, on_block_number)
        if balance_value is None:
            balance_value = self._get_balance_value_from_account_root_file(account, on_block_number)

        return balance_value

    def get_balance_lock(self, account: str, on_block_number: Optional[int] = None) -> str:
        if on_block_number is not None and on_block_number < -1:
            raise ValueError('block_number must be greater or equal to -1')

        lock = self._get_balance_lock_from_block(account, on_block_number)
        if lock:
            return lock

        lock = self._get_balance_lock_from_account_root_file(account, on_block_number)
        return account if lock is None else lock

    def get_last_account_root_file(self) -> Optional[AccountRootFile]:
        account_root_files = self.account_root_files
        if account_root_files:
            return account_root_files[-1]

        return None

    def get_first_account_root_file(self) -> Optional[AccountRootFile]:
        account_root_files = self.account_root_files
        if account_root_files:
            return account_root_files[0]

        return None

    def get_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        yield from self.account_root_files

    def get_account_root_files_reversed(self) -> Generator[AccountRootFile, None, None]:
        yield from reversed(self.account_root_files)
