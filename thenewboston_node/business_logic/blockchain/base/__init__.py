from datetime import datetime
from typing import Any, Optional, Type, TypeVar

from django.conf import settings

from thenewboston_node.core.utils.importing import import_from_string

from .account_state import AccountStateMixin
from .blockchain_state import BlockchainStateMixin
from .blocks import BlocksMixin
from .network import NetworkMixin
from .validation import ValidationMixin

T = TypeVar('T', bound='BlockchainBase')


# BlockchainBase is broken into several classes to reduce a single source code file size and simply navigation
# over the class code
class BlockchainBase(ValidationMixin, BlockchainStateMixin, BlocksMixin, AccountStateMixin, NetworkMixin):
    _instance = None

    def __init__(self, snapshot_period_in_blocks=None):
        self.snapshot_period_in_blocks = snapshot_period_in_blocks

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            blockchain_settings = settings.BLOCKCHAIN
            instance = cls.make_instance(blockchain_settings['class'], blockchain_settings.get('kwargs'))
            cls.set_instance_cache(instance)

        return instance

    @classmethod
    def make_instance(cls: Type[T], class_: str, kwargs: Optional[dict[str, Any]] = None):
        return import_from_string(class_)(**(kwargs or {}))

    @classmethod
    def set_instance_cache(cls: Type[T], instance: T):
        cls._instance = instance

    @classmethod
    def clear_instance_cache(cls):
        cls._instance = None

    def clear(self):
        raise NotImplementedError('Must be implemented in a child class')

    def utcnow(self):
        return datetime.utcnow()

    def is_empty(self):
        return not (self.has_blockchain_states() or self.has_blocks())
