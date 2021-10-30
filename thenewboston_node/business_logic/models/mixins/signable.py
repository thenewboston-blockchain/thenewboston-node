import logging
from dataclasses import dataclass, field, MISSING
from typing import Optional

from thenewboston_node.business_logic.models.mixins.message import MessageMixin
from thenewboston_node.business_logic.validators import validate_not_empty, validate_type
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import derive_public_key
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)


@revert_docstring
@dataclass
@cover_docstring
class OptionallySignableMixin:

    message: MessageMixin

    signer: Optional[hexstr] = field(
        default=MISSING, metadata={'example_value': '657cf373f6f8fb72854bd302269b8b2b3576e3e2a686bd7d0a112babaa1790c6'}
    )
    """Signer account number"""

    # We need signature to be optional to be able to create dataclass instance first and then sign it
    signature: Optional[hexstr] = field(
        default=MISSING,
        metadata={
            'example_value':
                '047185123de32d69184b93ae1f1d6a0228f0cfe477d7130f3318e620e481d4372090f013de5441278feda65ddd2b79daac62ee89870acb4834a27a1a10368b0b',
            'is_serialized_optional':
                False,
        }
    )
    """Message signature"""

    def sign(self, signing_key):
        verify_key = derive_public_key(signing_key)
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
        signature = self.signature
        if signature is None:
            return

        verify_key = self.validate_signer()
        validate_not_empty('Signature', signature)
        validate_type('Signature', signature, str)
        self.message.validate_signature(verify_key, signature)

    @validates('signer')
    def validate_signer(self):
        signer = self.signer
        if signer is None:
            return None

        validate_not_empty('Signer', signer)
        validate_type('Signer', signer, str)
        return signer


@revert_docstring
@dataclass
@cover_docstring
class SignableMixin(OptionallySignableMixin):
    signer: hexstr = field(
        metadata={'example_value': '657cf373f6f8fb72854bd302269b8b2b3576e3e2a686bd7d0a112babaa1790c6'}
    )
    """Signer account number"""

    @validates('signature')
    def validate_signature(self):
        signature = self.signature
        validate_not_empty('Signature', signature)
        super().validate_signature()

    @validates('signer')
    def validate_signer(self):
        signer = self.signer
        validate_not_empty('Signer', signer)
        return super().validate_signer()
