import logging
from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.mixins.message import MessageMixin
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import derive_verify_key

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class SignableMixin:

    signer: str
    """Signer's account number"""

    message: MessageMixin
    """Payload"""

    signature: Optional[str] = None
    """Signature of the message"""

    def sign(self, signing_key):
        verify_key = derive_verify_key(signing_key)
        stored_verify_key = self.signer
        if not stored_verify_key:
            logger.warning('Signing message with an empty signer')
        elif stored_verify_key != verify_key:
            logger.warning('Signer does not match with signing key')

        message_signature = self.message.generate_signature(signing_key)
        stored_message_signature = self.signature
        if stored_message_signature and stored_message_signature != message_signature:
            logger.warning('Overwriting existing message signature')

        self.signature = message_signature

    @validates('signature')
    def validate_signature(self):
        verify_key = self.validate_signer()
        signature = self.signature
        if not signature:
            raise ValidationError('Signature must be set')

        if not isinstance(signature, str):
            raise ValidationError('Signature  must be a string')

        self.message.validate_signature(verify_key, self.signature)

    @validates('signer')
    def validate_signer(self):
        signer = self.signer
        if not signer:
            raise ValidationError('Signer must be set')

        if not isinstance(signer, str):
            raise ValidationError('Signer must be a string')

        return signer
