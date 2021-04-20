import logging
from typing import Optional

import msgpack

from thenewboston_node.business_logic.exceptions import InvalidMessageSignatureError
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.collections import map_values, replace_keys
from thenewboston_node.core.utils.cryptography import (
    derive_verify_key, generate_signature, hash_normalized_dict, is_signature_valid
)

COMPACT_KEY_MAP = {
    # account root file
    'accounts': 'a',
    'last_block_number': 'lbn',
    'last_block_identifier': 'lbi',
    'last_block_timestamp': 'lbt',
    'next_block_identifier': 'nbi',
    # account balance
    'value': 'v',
    'lock': 'l',
    # block
    'node_identifier': 'ni',
    'message': 'm',
    'message_hash': 'mh',
    'message_signature': 'ms',
    # block message
    'transfer_request': 'tr',
    'timestamp': 't',
    'block_number': 'bn',
    'block_identifier': 'bi',
    'updated_balances': 'ub',
    # transfer request
    'sender': 's',
    # transfer request message
    'balance_lock': 'bl',
    # transaction
    'recipient': 'r',
    'amount': 'at',
    'fee': 'f',
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
    'node_identifier': hex_to_bytes,
    'message_hash': hex_to_bytes,
    'message_signature': hex_to_bytes,
    'block_identifier': hex_to_bytes,
    'balance_lock': hex_to_bytes,
    'recipient': hex_to_bytes,
    'sender': hex_to_bytes,
    'lock': hex_to_bytes,
}

UNCOMPACT_VALUE_MAP = {
    'node_identifier': bytes_to_hex,
    'message_hash': bytes_to_hex,
    'message_signature': bytes_to_hex,
    'block_identifier': bytes_to_hex,
    'balance_lock': bytes_to_hex,
    'recipient': bytes_to_hex,
    'sender': bytes_to_hex,
    'lock': bytes_to_hex,
}

COMPACT_SUBKEY_MAP = {
    'updated_balances': hex_to_bytes,
    'accounts': hex_to_bytes,
}

UNCOMPACT_SUBKEY_MAP = {
    'updated_balances': bytes_to_hex,
    'accounts': bytes_to_hex,
}

# Assert that bidirectional mapping is defined correctly
assert len(COMPACT_KEY_MAP) == len(UNCOMPACT_KEY_MAP)
assert COMPACT_KEY_MAP.keys() == set(UNCOMPACT_KEY_MAP.values())
assert UNCOMPACT_KEY_MAP.keys() == set(COMPACT_KEY_MAP.values())
assert set(COMPACT_VALUE_MAP.keys()) == set(UNCOMPACT_VALUE_MAP.keys())
assert set(COMPACT_SUBKEY_MAP.keys()) == set(UNCOMPACT_SUBKEY_MAP.keys())

logger = logging.getLogger(__name__)


class MessageMixin:

    def get_hash(self):
        normalized_message = self.get_normalized()
        message_hash = hash_normalized_dict(normalized_message)
        logger.debug('Got %s hash for message: %r', message_hash, normalized_message)
        return message_hash

    def generate_signature(self, signing_key):
        return generate_signature(signing_key, self.get_normalized())

    def validate_signature(self, verify_key: str, signature: str):
        if not is_signature_valid(verify_key, self.get_normalized(), signature):
            raise InvalidMessageSignatureError()

    def get_normalized(self) -> bytes:
        raise NotImplementedError('Must be implemented in a child class')


class SignableMixin:

    verify_key_field_name: Optional[str] = None

    message: MessageMixin

    def sign(self, signing_key):
        verify_key_field_name = self.verify_key_field_name
        if not verify_key_field_name:
            raise ValueError('`verify_key_field_name` class attribute must be set')

        verify_key = derive_verify_key(signing_key)
        stored_verify_key = getattr(self, verify_key_field_name, None)
        if not stored_verify_key:
            logger.warning('Signing message with empty `%s` value', verify_key_field_name)
        elif stored_verify_key != verify_key:
            logger.warning('`%s` value does not match with signing key', verify_key_field_name)

        message_signature = self.message.generate_signature(signing_key)
        stored_message_signature = self.message_signature
        if stored_message_signature and stored_message_signature != message_signature:
            logger.warning('Overwriting existing message signature')

        self.message_signature = message_signature

    @validates('signature')
    def validate_signature(self):
        verify_key_field_name = self.verify_key_field_name
        if not verify_key_field_name:
            raise ValueError('`verify_key_field_name` class attribute must be set')

        verify_key = getattr(self, verify_key_field_name)
        if not (verify_key and self.message_signature):
            raise InvalidMessageSignatureError()

        self.message.validate_signature(verify_key, self.message_signature)


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
