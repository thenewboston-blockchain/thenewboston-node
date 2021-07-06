from urllib.parse import urlparse

from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.misc import upper_first

from ..core.utils.types import hexstr
from .exceptions import ValidationError

HUMANIZED_TYPE_NAMES = {
    str: 'string',
    int: 'integer',
}

VALID_SCHEMES = ('http', 'https')


def validate_not_empty(subject, value):
    with validates(f'{subject} value'):
        if not value:
            raise ValidationError(upper_first(f'{subject} must be not empty'))


def validate_empty(subject, value):
    with validates(f'{subject} value'):
        if value:
            raise ValidationError(upper_first(f'{subject} must be empty'))


def validate_not_none(subject, value):
    with validates(f'{subject} value'):
        if value is None:
            raise ValidationError(upper_first(f'{subject} must be set'))


def validate_is_none(subject, value):
    with validates(f'{subject} value'):
        if value is not None:
            raise ValidationError(upper_first(f'{subject} must not be set'))


def validate_type(subject, value, type_):
    with validates(f'{subject} type'):
        if not isinstance(value, type_):
            raise ValidationError(upper_first(f'{subject} must be {HUMANIZED_TYPE_NAMES.get(type_, type_.__name__)}'))


def validate_min_item_count(subject, value, min_):
    with validates(f'{subject} item count'):
        if len(value) < min_:
            raise ValidationError(upper_first(f'{subject} must contain at least {min_} items'))


def validate_gte_value(subject, value, min_):
    with validates(f'{subject} value'):
        if value < min_:
            raise ValidationError(upper_first(f'{subject} must be greater or equal to {min_}'))


def validate_gt_value(subject, value, min_):
    with validates(f'{subject} value'):
        if value <= min_:
            raise ValidationError(upper_first(f'{subject} must be greater than {min_}'))


def validate_lte_value(subject, value, max_):
    with validates(f'{subject} value'):
        if value > max_:
            raise ValidationError(upper_first(f'{subject} must be less or equal to {max_}'))


def validate_lt_value(subject, value, max_):
    with validates(f'{subject} value'):
        if value >= max_:
            raise ValidationError(upper_first(f'{subject} must be less than {max_}'))


def validate_in(subject, value, value_set):
    with validates(f'{subject} value'):
        if value not in value_set:
            value_set_str = ', '.join(map(str, value_set))
            raise ValidationError(upper_first(f'{subject} must be one of {value_set_str}'))


def validate_greater_than_zero(subject, value):
    with validates(f'{subject} value'):
        if value <= 0:
            raise ValidationError(upper_first(f'{subject} must be greater than zero'))


def validate_exact_value(subject, value, expected_value):
    with validates(f'{subject} value'):
        if value != expected_value:
            raise ValidationError(upper_first(f'{subject} must be equal to {expected_value}'))


def validate_network_address(subject, value):
    with validates(f'{subject} value'):
        result = urlparse(value)
        validate_not_empty(f'{subject} scheme', result.scheme)
        validate_in(f'{subject} scheme', result.scheme, VALID_SCHEMES)
        validate_not_empty(f'{subject} hostname', result.hostname)


def validate_hexadecimal(subject, value):
    with validates(f'{subject} value'):
        try:
            hexstr(value).to_bytes()
        except ValueError:
            raise ValidationError(upper_first(f'{subject} must be hexadecimal string'))
