from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.dataclass import fake_super_methods


@fake_super_methods
@dataclass_json
@dataclass
class Transaction:
    recipient: str
    amount: int
    fee: Optional[str] = None

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()

        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        value = dict_.get('fee', SENTINEL)
        if value is None:
            del dict_['fee']

        return dict_
