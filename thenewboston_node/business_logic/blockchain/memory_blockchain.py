import copy
from itertools import islice
from typing import Optional

from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block

from .base import BlockchainBase


class MemoryBlockchain(BlockchainBase):
    """
    A blockchain implementation primarily for use in unittesting and being used as an example implementation
    """

    def __init__(self, *, initial_account_root_file):
        self.account_root_files = [AccountRootFile.from_dict(initial_account_root_file)]

        self.blocks: list[Block] = []

    def persist_block(self, block: Block):
        self.blocks.append(copy.deepcopy(block))

    def get_head_block(self) -> Optional[Block]:
        blocks = self.blocks
        if blocks:
            return blocks[-1]

        return None

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

        account_root_file = self.get_latest_account_root_file(start_block_number)
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

    def _get_balance_from_block(self, account: str, block_number: Optional[int] = None) -> Optional[int]:
        for block in self.get_blocks_until_account_root_file(block_number):
            balance = block.message.get_balance(account)
            if balance is not None:
                return balance.balance

        return None

    def _get_balance_from_account_root_file(self, account: str, block_number: Optional[int] = None) -> Optional[int]:
        return self.get_latest_account_root_file(block_number).get_balance_value(account)

    def get_account_balance(self, account: str, block_number: Optional[int] = None) -> Optional[int]:
        """
        Returns account balance for the specified account. If block_number is specified then
        the account balance for that block is returned (after the block_number block is applied)
        otherwise the current (head block) balance is returned. If block_number is equal to -1 then
        account balance before 0 block is returned.
        """
        if block_number is not None and block_number < -1:
            raise ValueError('block_number must be greater or equal to -1')

        balance = self._get_balance_from_block(account, block_number)
        if balance is None:
            balance = self._get_balance_from_account_root_file(account, block_number)

        return balance

    def get_account_balance_lock(self, account: str) -> str:
        for block in self.get_blocks_until_account_root_file():
            balance = block.message.get_balance(account)
            if balance is not None:
                balance_lock = balance.balance_lock
                if balance_lock:
                    return balance_lock

        return self.get_latest_account_root_file().get_balance_lock(account)

    def get_latest_account_root_file(self, before_block_number_inclusive: Optional[int] = None) -> AccountRootFile:
        if before_block_number_inclusive is not None and before_block_number_inclusive < -1:
            raise ValueError('before_block_number_inclusive must be greater or equal to -1')

        account_root_files = self.account_root_files
        assert account_root_files

        if before_block_number_inclusive is None:
            account_root_file = account_root_files[-1]
        elif before_block_number_inclusive == -1:
            account_root_file = account_root_files[0]
        else:
            for account_root_file in reversed(account_root_files):
                print(1, account_root_file)
                last_block_number = account_root_file.last_block_number
                if last_block_number is None or last_block_number <= before_block_number_inclusive:
                    break

        return copy.deepcopy(account_root_file)
