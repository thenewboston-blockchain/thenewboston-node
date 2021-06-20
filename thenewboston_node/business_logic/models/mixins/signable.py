import logging
from dataclasses import dataclass
from typing import Optional

from thenewboston_node.business_logic.models.mixins.message import MessageMixin
from thenewboston_node.business_logic.validators import validate_not_empty, validate_type
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import derive_verify_key
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)


@revert_docstring
@dataclass
@cover_docstring
class SignableMixin:

    signer: hexstr
    """Signer account number"""

    message: MessageMixin

    # We need signature to be optional to be able to create dataclass instance first and then sign it
    signature: Optional[hexstr] = None
    """Message signature"""

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
        validate_not_empty('Signature', signature)
        validate_type('Signature', signature, str)
        self.message.validate_signature(verify_key, self.signature)

    @validates('signer')
    def validate_signer(self):
        signer = self.signer
        validate_not_empty('Signer', signer)
        validate_type('Signer', signer, str)
        return signer
