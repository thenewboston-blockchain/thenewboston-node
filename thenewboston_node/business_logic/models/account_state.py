import logging
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.validators import validate_min_value, validate_not_empty, validate_type
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .mixins.misc import HumanizedClassNameMixin
from .node import Node

logger = logging.getLogger(__name__)


@fake_super_methods
@dataclass_json
@dataclass
class AccountState(HumanizedClassNameMixin):
    """Account state"""

    balance: Optional[int] = None  # type: ignore
    """Balance"""

    balance_lock: Optional[str] = None  # type: ignore
    """Balance lock"""

    node: Optional[Node] = None  # type: ignore
    """Network addresses"""

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()

        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        for name in self.__dataclass_fields__.keys():
            value = dict_.get(name, SENTINEL)
            if value is None:
                del dict_[name]

        return dict_

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
        validate_min_value(f'{self.humanized_class_name_lowered} balance', self.balance, 0)

    @validates()
    def validate_balance_lock(self):
        validate_not_empty(f'{self.humanized_class_name_lowered} balance_lock', self.balance_lock)
        validate_type(f'{self.humanized_class_name_lowered} balance_lock', self.balance_lock, str)

    @validates()
    def validate_node(self):
        return


# TODO(dmu) CRITICAL: Assert all attributes are optional
