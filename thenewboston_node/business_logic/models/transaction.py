import logging
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.constants import SENTINEL
from thenewboston_node.core.utils.dataclass import fake_super_methods

validation_logger = logging.getLogger(__name__ + '.validation_logger')


@fake_super_methods
@dataclass_json
@dataclass
class Transaction:
    recipient: str
    amount: int
    fee: Optional[bool] = None

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()

        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        value = dict_.get('fee', SENTINEL)
        if value in (None, False):
            del dict_['fee']

        return dict_

    def validate(self):
        validation_logger.debug('Validating %s', self)
        if not self.recipient:
            raise ValidationError('Transaction recipient is not set')
        validation_logger.debug('Transaction recipient is set (as expected)')

        amount = self.amount
        if not isinstance(amount, int):
            raise ValidationError('Transaction amount must be an integer')
        validation_logger.debug('Transaction amount is an integer')

        if amount < 1:
            raise ValidationError('Transaction amount must be greater or equal to 1')
        validation_logger.debug('Transaction amount is greater or equal to 1 (as expected)')

        if self.fee not in (True, False, None):
            raise ValidationError('Transaction fee value is invalid')
        validation_logger.debug('Transaction fee is valid')

        validation_logger.debug('%s is valid', self)
