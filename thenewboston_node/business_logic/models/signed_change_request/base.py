import copy
import logging
from dataclasses import dataclass
from typing import Type, TypeVar

from thenewboston_node.business_logic.models.base import BaseDataclass
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import derive_verify_key
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from ..mixins.signable import SignableMixin
from ..signed_change_request_message import SignedChangeRequestMessage

T = TypeVar('T', bound='SignedChangeRequest')

logger = logging.getLogger(__name__)


@revert_docstring
@dataclass
@cover_docstring
class SignedChangeRequest(SignableMixin, BaseDataclass):
    message: SignedChangeRequestMessage

    @classmethod
    def create_from_signed_change_request_message(
        cls: Type[T], message: SignedChangeRequestMessage, signing_key: hexstr
    ) -> T:
        request = cls(signer=derive_verify_key(signing_key), message=copy.deepcopy(message))
        request.sign(signing_key)
        return request

    @validates('signed request')
    def validate(self):
        self.validate_message()
        with validates('block signature'):
            self.validate_signature()

    @validates('signed request message')
    def validate_message(self):
        self.message.validate()
