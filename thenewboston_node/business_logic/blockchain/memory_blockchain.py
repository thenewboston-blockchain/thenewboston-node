import copy
from typing import Optional

from thenewboston_node.business_logic.exceptions import InvalidBlockError
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block

from .base import BlockchainBase


class MemoryBlockchain(BlockchainBase):
    """
    A blockchain implementation primarily for use in unittesting and being used as example implementation
    """

    def __init__(self, *, initial_account_root_file):
        self.account_root_files = [AccountRootFile.from_dict(initial_account_root_file)]

        self.blocks: list[Block] = []

    def add_block(self, block: Block):
        if not block.validate():
            raise InvalidBlockError()

        self.blocks.append(copy.deepcopy(block))

    def get_head_block(self) -> Optional[Block]:
        blocks = self.blocks
        if blocks:
            return blocks[-1]

        return None

    def get_blocks_until_last_account_root_file(self):
        last_account_root_file = self.get_last_account_root_file()
        account_root_file_block_identifier = last_account_root_file.last_block_identifier
        account_root_file_block_number = last_account_root_file.last_block_number

        for block in reversed(self.blocks):
            block_identifier = block.message.block_identifier
            assert block_identifier
            if block_identifier == account_root_file_block_identifier:
                # The block is already included in account root file, so we can and must stop search here
                # for performance and correct business logic reasons
                break

            assert account_root_file_block_number < block.message.block_number

            yield block

    def get_account_balance(self, account: str) -> Optional[int]:
        for block in self.get_blocks_until_last_account_root_file():
            balance = block.message.get_balance(account)
            if balance is not None:
                return balance.balance

        root_file_account_balance = self.get_last_account_root_file().accounts.get(account)
        if root_file_account_balance:
            return root_file_account_balance.balance

        return None

    def get_account_balance_lock(self, account: str) -> str:
        for block in self.get_blocks_until_last_account_root_file():
            balance = block.message.get_balance(account)
            if balance is not None:
                balance_lock = balance.balance_lock
                if balance_lock:
                    return balance_lock

        root_file_account_balance = self.get_last_account_root_file().get_balance(account)
        if root_file_account_balance:
            return root_file_account_balance.balance_lock

        return account

    def get_initial_account_root_file(self) -> AccountRootFile:
        return copy.deepcopy(self.account_root_files[0])

    def get_last_account_root_file(self) -> AccountRootFile:
        return copy.deepcopy(self.account_root_files[-1])
