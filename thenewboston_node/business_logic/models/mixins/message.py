import logging

from thenewboston_node.business_logic.exceptions import InvalidMessageSignatureError
from thenewboston_node.core.utils.cryptography import (
    generate_signature, hash_normalized_dict, is_signature_valid, normalize_dict
)
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)


class MessageMixin:

    def serialize_to_dict_for_cryptography(self):
        return self.serialize_to_dict()

    def get_normalized_for_cryptography(self) -> bytes:
        return normalize_dict(self.serialize_to_dict_for_cryptography())

    def get_hash(self) -> hexstr:
        normalized_message = self.get_normalized_for_cryptography()
        message_hash = hash_normalized_dict(normalized_message)
        logger.debug('Got %s hash for message: %r', message_hash, normalized_message)
        return message_hash

    def generate_signature(self, signing_key: hexstr):
        return generate_signature(signing_key, self.get_normalized_for_cryptography())

    def validate_signature(self, verify_key: hexstr, signature: hexstr):
        if not is_signature_valid(verify_key, self.get_normalized_for_cryptography(), signature):
            raise InvalidMessageSignatureError()
