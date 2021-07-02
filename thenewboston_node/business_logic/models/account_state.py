import logging
from dataclasses import dataclass, field
from typing import Optional

from thenewboston_node.business_logic.validators import validate_gte_value, validate_not_empty, validate_type
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from .base import BaseDataclass
from .node import Node

logger = logging.getLogger(__name__)


@revert_docstring
@dataclass
@cover_docstring
class AccountState(BaseDataclass):

    balance: Optional[int] = field(default=None, metadata={'example_value': 3000})  # type: ignore
    balance_lock: Optional[hexstr] = field(
        default=None, metadata={'example_value': 'ce20609f5c89dc9803f1c75a77c9e4b19b4f3c2c9cc690ff9966edd2b07d9130'}
    )  # type: ignore
    node: Optional[Node] = None  # type: ignore

    @classmethod
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, override=None):
        override = override or {}
        node_override = override.pop('node', None)
        if 'node' in dict_ and node_override:
            dict_ = dict_.copy()
            node_dict = dict_.pop('node')
            node_obj = Node.deserialize_from_dict(
                node_dict, complain_excessive_keys=complain_excessive_keys, override=node_override
            )
            override = override or {}
            override['node'] = node_obj

        return super().deserialize_from_dict(dict_, complain_excessive_keys=complain_excessive_keys, override=override)

    def get_attribute_value(self, attribute: str, account: str):
        value = getattr(self, attribute)
        if value is None:
            from thenewboston_node.business_logic.utils.blockchain import get_attribute_default_value
            return get_attribute_default_value(attribute, account)

        return value

    def get_balance_lock(self, account):
        return self.get_attribute_value('balance_lock', account)

    @validates()
    def validate(self):
        for name in self.__dataclass_fields__.keys():
            value = getattr(self, name)
            if value is not None:
                getattr(self, f'validate_{name}')()

    @validates()
    def validate_balance(self):
        validate_type(f'{self.humanized_class_name_lowered} balance', self.balance, int)
        validate_gte_value(f'{self.humanized_class_name_lowered} balance', self.balance, 0)

    @validates()
    def validate_balance_lock(self):
        validate_not_empty(f'{self.humanized_class_name_lowered} balance_lock', self.balance_lock)
        validate_type(f'{self.humanized_class_name_lowered} balance_lock', self.balance_lock, str)

    @validates()
    def validate_node(self):
        return


assert all(AccountState.is_optional_field(field) for field in AccountState.get_field_names())
