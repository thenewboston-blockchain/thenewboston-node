import copy
from typing import Optional

from thenewboston_node.business_logic.models.block import Block

from .base import BlockchainBase


class MemoryBlockchain(BlockchainBase):
    """
    A blockchain implementation primarily for use in unittesting
    """

    def __init__(self, *, initial_account_root_file):
        self.initial_account_root_file = initial_account_root_file

        self.blocks: list[Block] = []

    def add_block(self, block: Block):
        self.blocks.append(copy.deepcopy(block))

    def get_head_block(self) -> Optional[Block]:
        blockchain = self.blocks
        if blockchain:
            return blockchain[-1]

        return None

    def get_account_balance(self, account: str) -> Optional[int]:
        for block in self.blocks:
            for balance in block.message.updated_balances:
                if balance.account == account:
                    return balance.balance

        return None

    def get_account_balance_lock(self, account: str) -> str:
        for block in self.blocks:
            for balance in block.message.updated_balances:
                if balance.account == account and balance.balance_lock:
                    balance_lock = balance.balance_lock
                    if balance_lock:
                        return balance_lock

        return account

    def get_initial_account_root_file(self) -> dict:
        return self.initial_account_root_file.copy()
