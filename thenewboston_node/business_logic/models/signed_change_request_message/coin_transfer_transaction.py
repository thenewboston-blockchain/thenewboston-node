from dataclasses import dataclass
from typing import Optional

from django.conf import settings

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.validators import (
    validate_gte_value, validate_in, validate_not_empty, validate_type
)
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.misc import humanize_camel_case
from thenewboston_node.core.utils.types import hexstr

from ..base import BaseDataclass


@dataclass
class CoinTransferTransaction(BaseDataclass):
    """Coin transfer between accounts"""

    recipient: hexstr
    """Recipient account number"""

    amount: int

    # TODO(dmu) HIGH: Rename to `is_fee`
    fee: Optional[bool] = False  # None value won't be serialized
    """Set if transaction is fee"""

    memo: Optional[str] = None

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
        amount = self.amount

        validate_not_empty(f'{self.humanized_class_name} recipient', self.recipient)
        validate_type(f'{self.humanized_class_name} amount', amount, int)
        validate_gte_value(f'{self.humanized_class_name} amount', amount, 1)
        validate_in(f'{self.humanized_class_name} fee', self.fee, (True, False, None))

        with validates('memo'):
            max_len = settings.MEMO_MAX_LENGTH
            if self.memo and len(self.memo) > max_len:
                raise ValidationError(f'{self.humanized_class_name} memo must be less than {max_len} characters')
