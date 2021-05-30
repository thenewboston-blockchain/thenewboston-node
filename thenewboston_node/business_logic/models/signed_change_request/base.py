import copy
import logging
from dataclasses import dataclass
from typing import Type, TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import derive_verify_key
from thenewboston_node.core.utils.dataclass import fake_super_methods

from ..mixins.misc import HumanizedClassNameMixin
from ..mixins.signable import SignableMixin
from ..signed_change_request_message import SignedChangeRequestMessage

T = TypeVar('T', bound='SignedChangeRequest')

logger = logging.getLogger(__name__)


@fake_super_methods
@dataclass_json
@dataclass
class SignedChangeRequest(SignableMixin, HumanizedClassNameMixin):
    message: SignedChangeRequestMessage
    """Request payload"""

    @classmethod
    def create_from_signed_change_request_message(
        cls: Type[T], message: SignedChangeRequestMessage, signing_key: str
    ) -> T:
        request = cls(signer=derive_verify_key(signing_key), message=copy.deepcopy(message))
        request.sign(signing_key)
        return request

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['message'] = self.message.to_dict()
        return dict_

    @validates('signed request')
    def validate(self):
        self.validate_message()
        with validates('block signature'):
            self.validate_signature()

    @validates('signed request message')
    def validate_message(self):
        self.message.validate()
