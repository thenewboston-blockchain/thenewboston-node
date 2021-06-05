from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.misc import upper_first

from .exceptions import ValidationError

HUMANIZED_TYPE_NAMES = {
    str: 'string',
    int: 'integer',
}


def validate_not_empty(subject, value):
    with validates(f'{subject} value'):
        if not value:
            raise ValidationError(upper_first(f'{subject} must be not empty'))


def validate_empty(subject, value):
    with validates(f'{subject} value'):
        if value:
            raise ValidationError(upper_first(f'{subject} must be empty'))


def validate_type(subject, value, type_):
    with validates(f'{subject} type'):
        if not isinstance(value, type_):
            raise ValidationError(upper_first(f'{subject} must be {HUMANIZED_TYPE_NAMES.get(type_, type_.__name__)}'))


def validate_min_item_count(subject, value, min_):
    with validates(f'{subject} item count'):
        if len(value) < min_:
            raise ValidationError(upper_first(f'{subject} must contain at least {min_} items'))


def validate_min_value(subject, value, min_):
    with validates(f'{subject} value'):
        if value < min_:
            raise ValidationError(upper_first(f'{subject} must be greater or equal to {min_}'))


def validate_greater_than_zero(subject, value):
    with validates(f'{subject} value'):
        if value <= 0:
            raise ValidationError(upper_first(f'{subject} must be greater than zero'))


def validate_exact_value(subject, value, expected_value):
    with validates(f'{subject} value'):
        if value != expected_value:
            raise ValidationError(upper_first(f'{subject} must be equal to {expected_value}'))
