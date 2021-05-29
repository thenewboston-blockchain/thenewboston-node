import logging
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.dataclass import fake_super_methods

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class AccountState:
    """Account state"""

    balance: int
    """Balance"""

    balance_lock: str
    """Balance lock"""

    @validates('account state')
    def validate(self, validate_lock=True):
        with validates('account state attributes'):
            with validates('account balance'):
                if not isinstance(self.balance, int):
                    raise ValidationError('Account balance must be an integer')

                if self.balance < 0:
                    raise ValidationError('Account balance must be a positive integer')

            if validate_lock:
                with validates('account lock'):
                    if not isinstance(self.balance_lock, str):
                        raise ValidationError('Account lock must be a string')

                    if not self.balance_lock:
                        raise ValidationError('Account lock must be set')


@fake_super_methods
@dataclass_json
@dataclass
class AccountStateUpdate(AccountState):
    """Account balance state when block is validated"""

    balance_lock: Optional[str] = None  # type: ignore

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()

        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        value = dict_.get('balance_lock', SENTINEL)
        if value is None:
            del dict_['balance_lock']

        return dict_

    @validates('block account balance')
    def validate(self):
        super().validate(validate_lock=False)
