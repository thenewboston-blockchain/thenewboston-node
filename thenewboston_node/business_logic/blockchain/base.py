from typing import Optional

from ..models.block import Block


class Blockchain:

    def get_account_balance(self, account: str) -> Optional[int]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_account_balance_lock(self, account: str) -> str:
        raise NotImplementedError('Must be implemented in a child class')

    def get_head_block(self) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_genesis_block_identifier(self) -> str:
        return self.get_initial_account_root_file_hash()

    def get_initial_account_root_file_hash(self) -> str:
        raise NotImplementedError('Must be implemented in a child class')
