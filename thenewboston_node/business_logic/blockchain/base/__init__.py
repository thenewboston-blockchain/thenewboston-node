from datetime import datetime
from typing import Type, TypeVar

from django.conf import settings

from thenewboston_node.core.utils.importing import import_from_string

from .account_state import AccountStateMixin
from .blockchain_state import BlockchainStateMixin
from .blocks import BlocksMixin
from .validation import ValidationMixin

T = TypeVar('T', bound='BlockchainBase')


# BlockchainBase is broken into several classes to reduce a single source code file size and simply navigation
# over the class code
class BlockchainBase(ValidationMixin, BlockchainStateMixin, BlocksMixin, AccountStateMixin):
    _instance = None

    def __init__(self, snapshot_period_in_blocks=None):
        self.snapshot_period_in_blocks = snapshot_period_in_blocks

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

    def utcnow(self):
        return datetime.utcnow()
