from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import constants
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.dataclass import fake_super_methods
from thenewboston_node.core.utils.misc import humanize_camel_case

from ..mixins.misc import HumanizedClassNameMixin


# TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
def remove_key_if_optional(dict_, key, optional_values=(None,)):
    value = dict_.get(key, SENTINEL)
    if value in optional_values:
        del dict_[key]


@fake_super_methods
@dataclass_json
@dataclass
class CoinTransferTransaction(HumanizedClassNameMixin):
    recipient: str
    amount: int
    fee: Optional[bool] = None  # None value won't be serialized
    memo: Optional[str] = None

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()

        remove_key_if_optional(dict_, key='fee', optional_values=(None, False))
        remove_key_if_optional(dict_, key='memo', optional_values=(None,))

        return dict_

    @property
    def humanized_class_name(self):
        return humanize_camel_case(self.__class__.__name__)

    @validates('transaction {}')
    def validate(self):
        with validates('recipient'):
            if not self.recipient:
                raise ValidationError(f'{self.humanized_class_name} recipient is not set')

        with validates('amount'):
            amount = self.amount
            if not isinstance(amount, int):
                raise ValidationError(f'{self.humanized_class_name} amount must be an integer')

            if amount < 1:
                raise ValidationError(f'{self.humanized_class_name} amount must be greater or equal to 1')

        with validates('fee'):
            if self.fee not in (True, False, None):
                raise ValidationError(f'{self.humanized_class_name} fee value is invalid')

        with validates('memo'):
            max_len = constants.MEMO_MAX_LENGTH
            if self.memo and len(self.memo) > max_len:
                raise ValidationError(f'{self.humanized_class_name} memo must be less than {max_len} characters')
