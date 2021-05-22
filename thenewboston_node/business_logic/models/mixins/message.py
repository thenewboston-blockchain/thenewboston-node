import logging

from thenewboston_node.business_logic.exceptions import InvalidMessageSignatureError
from thenewboston_node.core.utils.cryptography import generate_signature, hash_normalized_dict, is_signature_valid

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
