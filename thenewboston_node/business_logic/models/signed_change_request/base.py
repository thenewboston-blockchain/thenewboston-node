import copy
import logging
from dataclasses import dataclass
from typing import Any, Optional, Type, TypeVar

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.base import BaseDataclass
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import derive_public_key
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
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, override: Optional[dict[str, Any]] = None):
        from . import SIGNED_CHANGE_REQUEST_TYPE_MAP

        # TODO(dmu) MEDIUM: This polymorphic deserializer duplicates the logic in Block/BlockMessage.
        #                   Consider keeping only this serializer
        # TODO(dmu) MEDIUM: Maybe we do not really need to subclass SignedChangeRequest, but
        #                   subclassing of SignedChangeRequestMessage is enough
        signed_change_request_type = (dict_.get('message') or {}).get('signed_change_request_type')
        if cls == SignedChangeRequest:
            class_ = SIGNED_CHANGE_REQUEST_TYPE_MAP.get(signed_change_request_type)
            if class_ is None:
                raise ValidationError('message.signed_change_request_type must be provided')

            return class_.deserialize_from_dict(dict_, complain_excessive_keys=complain_excessive_keys)  # type: ignore

        if signed_change_request_type:
            class_ = SIGNED_CHANGE_REQUEST_TYPE_MAP.get(signed_change_request_type)
            if class_ is None:
                raise ValidationError(f'Unsupported signed_change_request_type: {signed_change_request_type}')

            if not issubclass(cls, class_):
                raise ValidationError(
                    f'{cls} does not match with signed_change_request_type: {signed_change_request_type}'
                )

        return super().deserialize_from_dict(dict_, complain_excessive_keys=complain_excessive_keys)

    @classmethod
    def create_from_signed_change_request_message(
        cls: Type[T], message: SignedChangeRequestMessage, signing_key: hexstr
    ) -> T:
        request = cls(signer=derive_public_key(signing_key), message=copy.deepcopy(message))
        request.sign(signing_key)
        return request

    @validates('signed request')
    def validate(self, blockchain, block_number: int):
        self.validate_message()
        with validates('block signature'):
            self.validate_signature()

    @validates('signed request message')
    def validate_message(self):
        self.message.validate()

    def get_updated_account_states(self, blockchain):
        raise NotImplementedError('Must be implemented in subclass')
