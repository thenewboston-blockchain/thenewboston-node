import logging
from typing import Optional

from thenewboston_node.core.utils.cryptography import (
    derive_verify_key, generate_signature, hash_normalized_message, is_signature_valid
)

logger = logging.getLogger(__name__)


class MessageMixin:

    def get_hash(self):
        normalized_message = self.get_normalized()
        message_hash = hash_normalized_message(normalized_message)
        logger.debug('Got %s hash for message: %r', message_hash, normalized_message)
        return message_hash

    def generate_signature(self, signing_key):
        return generate_signature(signing_key, self.get_normalized())

    def is_signature_valid(self, verify_key: str, signature: str) -> bool:
        return is_signature_valid(verify_key, self.get_normalized(), signature)

    def get_normalized(self) -> bytes:
        raise NotImplementedError('Must be implemented in a child class')


class SignableMixin:

    verify_key_field_name = Optional[str]

    def sign(self, signing_key):
        verify_key_field_name = self.verify_key_field_name
        assert verify_key_field_name

        verify_key = derive_verify_key(signing_key)
        stored_verify_key = getattr(self, verify_key_field_name, None)
        if stored_verify_key and stored_verify_key != verify_key:
            logger.warning('`%s` value does not match with signing key', verify_key_field_name)

        setattr(self, verify_key_field_name, verify_key)

        message_signature = self.message.generate_signature(signing_key)
        stored_message_signature = self.message_signature
        if stored_message_signature and stored_message_signature != message_signature:
            logger.warning('Overwriting existing message signature')

        self.message_signature = message_signature
