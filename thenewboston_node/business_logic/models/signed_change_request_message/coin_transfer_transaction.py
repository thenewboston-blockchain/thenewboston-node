from dataclasses import dataclass
from typing import Optional

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import constants
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.misc import humanize_camel_case

from ..base import BaseDataclass
from ..mixins.misc import HumanizedClassNameMixin


@dataclass
class CoinTransferTransaction(HumanizedClassNameMixin, BaseDataclass):
    """Coin transfer between accounts"""

    recipient: str
    """Recipient's account number"""

    amount: int
    """Coins being sent to the recipient"""

    # TODO(dmu) HIGH: Rename to `is_fee`
    fee: Optional[bool] = False  # None value won't be serialized
    """Set if transaction is fee"""

    memo: Optional[str] = None
    """Optional memo"""

    @classmethod
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, override=None):
        deserialized = super().deserialize_from_dict(
            dict_, complain_excessive_keys=complain_excessive_keys, override=override
        )

        # TODO(dmu) CRITICAL: Fix fee workaround
        if deserialized.fee is None:
            deserialized.fee = False

        return deserialized

    def serialize_to_dict(self, skip_none_values=True, coerce_to_json_types=True, exclude=()):
        serialized = super().serialize_to_dict(
            skip_none_values=skip_none_values,
            coerce_to_json_types=coerce_to_json_types,
            exclude=exclude,
        )
        if serialized.get('fee', SENTINEL) in (None, False):
            del serialized['fee']

        return serialized

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
