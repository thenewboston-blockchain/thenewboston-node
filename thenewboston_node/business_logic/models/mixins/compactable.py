import logging
import typing

import msgpack

from thenewboston_node.business_logic.validators import validate_not_none
from thenewboston_node.core.utils.collections import replace_keys
from thenewboston_node.core.utils.types import hexstr

from .serializable import SerializableMixin

COMPACT_KEY_MAP = {
    'account_states': 'a',
    'last_block_number': 'ln',
    'last_block_identifier': 'li',
    'last_block_timestamp': 'lt',
    'next_block_identifier': 'ni',
    'balance': 'b',
    'balance_lock': 'bl',
    'message': 'm',
    'hash': 'h',
    'signed_change_request': 'tr',
    'timestamp': 'ts',
    'block_number': 'bn',
    'block_identifier': 'bi',
    'block_type': 'bt',
    'updated_account_states': 'u',
    'network_addresses': 'na',
    'recipient': 'r',
    'amount': 'at',
    'is_fee': 'f',
    'memo': 'mm',
    'signer': 's',
    'signature': 'si',
    'node': 'n',
    'fee_amount': 'fa',
    'fee_account': 'fac',
    'txs': 't',
    'primary_validator_schedule': 'pv',
    'begin_block_number': 'bb',
    'end_block_number': 'eb',
}

UNCOMPACT_KEY_MAP = {value: key for key, value in COMPACT_KEY_MAP.items()}

# Assert that bidirectional mapping is defined correctly
assert len(COMPACT_KEY_MAP) == len(UNCOMPACT_KEY_MAP)
assert COMPACT_KEY_MAP.keys() == set(UNCOMPACT_KEY_MAP.values())
assert UNCOMPACT_KEY_MAP.keys() == set(COMPACT_KEY_MAP.values())

logger = logging.getLogger(__name__)


def compact_key(key):
    return COMPACT_KEY_MAP.get(key, key)


def get_type_compact_transform_map():
    return {
        CompactableMixin: lambda type_, value: type_.to_compact_values(value),
        hexstr: lambda type_, value: hexstr(value).to_bytes(),
    }


def get_type_uncompact_transform_map():
    return {
        CompactableMixin: lambda type_, value: type_.from_compact_values(value),
        hexstr: lambda type_, value: type_.from_bytes(value),
    }


def transform_value(value, type_, transform_map):
    type_origin = typing.get_origin(type_)
    type_args = typing.get_args(type_)

    for transform_type, transform_func in transform_map.items():
        if issubclass(type_, transform_type):
            return transform_func(type_, value)

    if type_origin and issubclass(type_origin, dict):
        new_value = {}
        for item_key, item_value in value.items():
            item_key_type, item_value_type = type_args

            item_key = transform_value(item_key, item_key_type, transform_map)
            item_value = transform_value(item_value, item_value_type, transform_map)
            new_value[item_key] = item_value
        return new_value
    elif type_origin and issubclass(type_origin, list):
        new_value = []
        for item in value:
            item_type = type_args[0]
            item_value = transform_value(item, item_type, transform_map)
            new_value.append(item_value)
        return new_value
    else:
        return value


class CompactableMixin(SerializableMixin):

    @classmethod
    def from_compact_dict(cls, compact_dict, compact_keys=True, compact_values=True):
        dict_ = compact_dict

        if compact_keys:
            dict_ = replace_keys(dict_, UNCOMPACT_KEY_MAP)

        if compact_values:
            dict_ = cls.from_compact_values(dict_)

        return cls.deserialize_from_dict(dict_)

    def to_compact_dict(self, compact_keys=True, compact_values=True):
        dict_ = self.serialize_to_dict()
        if compact_values:
            dict_ = self.to_compact_values(dict_)

        if compact_keys:
            dict_ = replace_keys(dict_, COMPACT_KEY_MAP)

        return dict_

    @classmethod
    def to_compact_values(cls, dict_):
        return cls._transform_dict(dict_, transform_map=get_type_compact_transform_map())

    @classmethod
    def from_compact_values(cls, dict_):
        return cls._transform_dict(dict_, transform_map=get_type_uncompact_transform_map())

    @classmethod
    def _transform_dict(cls, dict_, transform_map):
        field_types = cls.get_field_types(dict_)

        new_dict = {}
        for key, value in dict_.items():
            type_ = field_types.get(key)
            validate_not_none(f'{cls.__name__} {key} type', type_)
            value = transform_value(value, type_, transform_map)
            new_dict[key] = value

        return new_dict

    @classmethod
    def get_field_types(cls, dict_) -> typing.Dict[str, typing.Type]:
        return {field_name: cls.get_field_type(field_name) for field_name in dict_}


class MessagpackCompactableMixin(CompactableMixin):

    @classmethod
    def from_messagepack(cls, messagepack_binary: bytes, compact_keys=True, compact_values=True):
        unpacked = msgpack.unpackb(messagepack_binary)
        return cls.from_compact_dict(unpacked, compact_keys=compact_keys, compact_values=compact_values)

    def to_messagepack(self, compact_keys=True, compact_values=True):
        compact_dict = self.to_compact_dict(compact_keys=compact_keys, compact_values=compact_values)
        return msgpack.packb(compact_dict)
