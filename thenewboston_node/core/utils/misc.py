import re

import yaml


class Default(dict):

    def __missing__(self, key):
        return '<default>'


def hex_to_bytes(hex_string: str) -> bytes:
    return bytes.fromhex(hex_string)


def bytes_to_hex(bytes_: bytes) -> str:
    return bytes(bytes_).hex()


def upper_first(value):
    # value.capitalize() also lowers all other letters, so we upper_first() function
    return value[:1].upper() + value[1:]


def humanize_camel_case(value, apply_upper_first=True):
    value = re.sub(r'(?<!^)(?=[A-Z])', ' ', value).lower()
    if apply_upper_first:
        value = upper_first(value)

    return value


def humanize_snake_case(value, apply_upper_first=True):
    value = value.replace('_', ' ')
    if apply_upper_first:
        value = upper_first(value)

    return value


def yaml_coerce(value):
    if isinstance(value, str):
        return yaml.load('dummy: ' + value, Loader=yaml.SafeLoader)['dummy']

    return value
