from typing import Optional, Type, TypeVar

from django.conf import settings

from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.core.utils.importing import import_from_string

from ..models.block import Block

T = TypeVar('T', bound='BlockchainBase')


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
        raise NotImplementedError('Must be implemented in a child class')

    def get_account_balance(self, account: str) -> Optional[int]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_account_balance_lock(self, account: str) -> str:
        raise NotImplementedError('Must be implemented in a child class')

    def get_head_block(self) -> Optional[Block]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_next_block_identifier(self) -> str:
        head_block = self.get_head_block()
        if head_block:
            message_hash = head_block.message_hash
            assert message_hash
            return message_hash

        return self.get_last_account_root_file().get_next_block_identifier()

    def get_next_block_number(self) -> int:
        head_block = self.get_head_block()
        if head_block:
            return head_block.message.block_number + 1

        return self.get_last_account_root_file().get_next_block_number()

    def get_initial_account_root_file(self) -> AccountRootFile:
        raise NotImplementedError('Must be implemented in a child class')

    def get_last_account_root_file(self) -> AccountRootFile:
        raise NotImplementedError('Must be implemented in a child class')

    def validate(self):
        # Validations to be implemented:
        # 1. Block numbers are sequential
        # 2. Block identifiers equal to previous block message hash
        raise NotImplementedError('TO BE implemented')
