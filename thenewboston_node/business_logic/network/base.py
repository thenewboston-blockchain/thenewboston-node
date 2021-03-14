from typing import Type, TypeVar

from django.conf import settings

from thenewboston_node.business_logic.models.node import Node, PrimaryValidator
from thenewboston_node.core.utils.importing import import_from_string

T = TypeVar('T', bound='NetworkBase')


class NetworkBase:
    _instance = None

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            blockchain_settings = settings.NETWORK
            class_ = import_from_string(blockchain_settings['class'])
            instance = class_(**(blockchain_settings.get('kwargs') or {}))
            cls._instance = instance

        return instance

    @classmethod
    def clear_instance_cache(cls):
        cls._instance = None

    def get_primary_validator(self) -> PrimaryValidator:
        raise NotImplementedError('Must be implemented in a child class')

    def get_nodes(self, include_primary_validator=False) -> list[Node]:
        raise NotImplementedError('Must be implemented in a child class')

    def get_preferred_node(self) -> Node:
        raise NotImplementedError('Must be implemented in a child class')
