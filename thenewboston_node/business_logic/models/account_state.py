import logging
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.logging import validates

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
