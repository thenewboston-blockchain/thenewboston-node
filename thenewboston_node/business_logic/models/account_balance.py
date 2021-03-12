from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.dataclass import fake_super_methods


@fake_super_methods
@dataclass_json
@dataclass
class AccountBalance:
    account: str
    balance: int
    balance_lock: Optional[str] = None

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()

        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        value = dict_.get('balance_lock', SENTINEL)
        if value is None:
            del dict_['balance_lock']

        return dict_
