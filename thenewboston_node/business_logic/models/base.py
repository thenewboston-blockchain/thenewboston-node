import logging
from typing import Optional

import msgpack

from thenewboston_node.business_logic.exceptions import InvalidMessageSignatureError
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.collections import replace_keys
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

# Assert that bidirectional mapping is defined correctly
assert len(COMPACT_KEY_MAP) == len(UNCOMPACT_KEY_MAP)
assert COMPACT_KEY_MAP.keys() == set(UNCOMPACT_KEY_MAP.values())
assert UNCOMPACT_KEY_MAP.keys() == set(COMPACT_KEY_MAP.values())

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
    def from_compact_dict(cls, compact_dict):
        return cls.from_dict(replace_keys(compact_dict, UNCOMPACT_KEY_MAP))

    def to_compact_dict(self):
        return replace_keys(self.to_dict(), COMPACT_KEY_MAP)


class MessagpackCompactableMixin(CompactableMixin):

    @classmethod
    def from_messagepack(cls, messagepack_binary: bytes):
        return cls.from_compact_dict(msgpack.unpackb(messagepack_binary))

    def to_messagepack(self):
        return msgpack.packb(self.to_compact_dict())
