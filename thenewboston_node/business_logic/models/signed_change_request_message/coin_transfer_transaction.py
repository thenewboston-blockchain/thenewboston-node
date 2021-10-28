from dataclasses import dataclass, field
from typing import Optional

from django.conf import settings

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.validators import (
    validate_gte_value, validate_in, validate_not_empty, validate_type
)
from thenewboston_node.core.constants import SENTINEL
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.misc import humanize_camel_case
from thenewboston_node.core.utils.types import hexstr

from ..base import BaseDataclass


@revert_docstring
@dataclass
@cover_docstring
class CoinTransferTransaction(BaseDataclass):

    recipient: hexstr = field(
        metadata={'example_value': '7584e5ad3f3d29f44179be133790dc94b52dd2e671b9b96694faa36bcc14c135'}
    )
    """Recipient account number"""

    amount: int = field(metadata={'example_value': 1200})
    is_fee: Optional[bool] = field(default=False, metadata={'example_value': True})
    """Is fee?"""

    memo: Optional[str] = field(default=None, metadata={'example_value': 'For candy'})

    @classmethod
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, override=None):
        deserialized = super().deserialize_from_dict(
            dict_, complain_excessive_keys=complain_excessive_keys, override=override
        )

        # TODO(dmu) CRITICAL: Fix is_fee workaround
        if deserialized.is_fee is None:
            deserialized.is_fee = False

        return deserialized

    def serialize_to_dict(self, skip_none_values=True, coerce_to_json_types=True, exclude=()):
        serialized = super().serialize_to_dict(
            skip_none_values=skip_none_values,
            coerce_to_json_types=coerce_to_json_types,
            exclude=exclude,
        )
        if serialized.get('is_fee', SENTINEL) in (None, False):
            del serialized['is_fee']

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
        validate_in(f'{self.humanized_class_name} is_fee', self.is_fee, (True, False, None))

        with validates('memo'):
            max_len = settings.MEMO_MAX_LENGTH
            if self.memo and len(self.memo) > max_len:
                raise ValidationError(f'{self.humanized_class_name} memo must be less than {max_len} characters')
