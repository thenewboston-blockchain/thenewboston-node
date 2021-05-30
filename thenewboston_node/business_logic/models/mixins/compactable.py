import logging

import msgpack

from thenewboston_node.core.utils.collections import map_values, replace_keys

COMPACT_KEY_MAP = {
    # account root file
    'account_states': 'a',
    'last_block_number': 'ln',
    'last_block_identifier': 'li',
    'last_block_timestamp': 'lt',
    'next_block_identifier': 'ni',
    # account balance
    'balance': 'b',
    'balance_lock': 'bl',
    # block
    'message': 'm',
    'message_hash': 'mh',
    # block message
    'signed_change_request': 'tr',
    'timestamp': 't',
    'block_number': 'bn',
    'block_identifier': 'bi',
    'updated_account_states': 'u',
    'network_addresses': 'na',
    # transaction
    'recipient': 'r',
    'amount': 'at',
    'fee': 'f',
    'memo': 'mm',
    # common
    'signer': 's',
    'signature': 'si',
}

UNCOMPACT_KEY_MAP = {value: key for key, value in COMPACT_KEY_MAP.items()}


def hex_to_bytes(value):
    if value is None:
        return value
    return bytes.fromhex(value)


def bytes_to_hex(value):
    if value is None:
        return value
    return value.hex()


COMPACT_VALUE_MAP = {
    'signer': hex_to_bytes,
    'message_hash': hex_to_bytes,
    'signature': hex_to_bytes,
    'block_identifier': hex_to_bytes,
    'balance_lock': hex_to_bytes,
    'recipient': hex_to_bytes,
}

UNCOMPACT_VALUE_MAP = {
    'signer': bytes_to_hex,
    'message_hash': bytes_to_hex,
    'signature': bytes_to_hex,
    'block_identifier': bytes_to_hex,
    'balance_lock': bytes_to_hex,
    'recipient': bytes_to_hex,
}

COMPACT_SUBKEY_MAP = {
    'updated_account_states': hex_to_bytes,
    'account_states': hex_to_bytes,
}

UNCOMPACT_SUBKEY_MAP = {
    'updated_account_states': bytes_to_hex,
    'account_states': bytes_to_hex,
}

# Assert that bidirectional mapping is defined correctly
assert len(COMPACT_KEY_MAP) == len(UNCOMPACT_KEY_MAP)
assert COMPACT_KEY_MAP.keys() == set(UNCOMPACT_KEY_MAP.values())
assert UNCOMPACT_KEY_MAP.keys() == set(COMPACT_KEY_MAP.values())
assert set(COMPACT_VALUE_MAP.keys()) == set(UNCOMPACT_VALUE_MAP.keys())
assert set(COMPACT_SUBKEY_MAP.keys()) == set(UNCOMPACT_SUBKEY_MAP.keys())

logger = logging.getLogger(__name__)


class CompactableMixin:

    @classmethod
    def from_compact_dict(cls, compact_dict, compact_keys=True, compact_values=True):
        dict_ = compact_dict
        if compact_keys:
            dict_ = replace_keys(dict_, UNCOMPACT_KEY_MAP)
        if compact_values:
            dict_ = map_values(dict_, UNCOMPACT_VALUE_MAP)
            dict_ = map_values(dict_, UNCOMPACT_SUBKEY_MAP, subkeys=True)
        return cls.from_dict(dict_)

    def to_compact_dict(self, compact_keys=True, compact_values=True):
        dict_ = self.to_dict()
        if compact_values:
            dict_ = map_values(dict_, COMPACT_VALUE_MAP)
            dict_ = map_values(dict_, COMPACT_SUBKEY_MAP, subkeys=True)
        if compact_keys:
            dict_ = replace_keys(dict_, COMPACT_KEY_MAP)
        return dict_


class MessagpackCompactableMixin(CompactableMixin):

    @classmethod
    def from_messagepack(cls, messagepack_binary: bytes, compact_keys=True, compact_values=True):
        unpacked = msgpack.unpackb(messagepack_binary)
        return cls.from_compact_dict(unpacked, compact_keys=compact_keys, compact_values=compact_values)

    def to_messagepack(self, compact_keys=True, compact_values=True):
        compact_dict = self.to_compact_dict(compact_keys=compact_keys, compact_values=compact_values)
        return msgpack.packb(compact_dict)
