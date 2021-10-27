import copy
from dataclasses import dataclass, field
from typing import Any, Optional

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.base import BaseDataclass
from thenewboston_node.business_logic.models.constants import BlockType
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring

from ..mixins.message import MessageMixin


@revert_docstring
@dataclass
@cover_docstring
class SignedChangeRequestMessage(MessageMixin, BaseDataclass):

    signed_change_request_type: str = field(metadata={'example_value': BlockType.COIN_TRANSFER.value})

    @classmethod
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, override: Optional[dict[str, Any]] = None):
        from . import SIGNED_CHANGE_REQUEST_MESSAGE_TYPE_MAP

        dict_copy = copy.deepcopy(dict_)
        signed_change_request_type = dict_copy.pop('signed_change_request_type', None)
        if cls == SignedChangeRequestMessage:
            class_ = SIGNED_CHANGE_REQUEST_MESSAGE_TYPE_MAP.get(signed_change_request_type)
            if class_ is None:
                raise ValidationError('signed_change_request_type must be provided')

            return class_.deserialize_from_dict(  # type: ignore
                dict_copy, complain_excessive_keys=complain_excessive_keys
            )

        if signed_change_request_type:
            class_ = SIGNED_CHANGE_REQUEST_MESSAGE_TYPE_MAP.get(signed_change_request_type)
            if class_ is None:
                raise ValidationError(f'Unsupported signed_change_request_type: {signed_change_request_type}')

            if not issubclass(cls, class_):
                raise ValidationError(
                    f'{cls} does not match with signed_change_request_type: {signed_change_request_type}'
                )

        return super().deserialize_from_dict(dict_copy, complain_excessive_keys=complain_excessive_keys)

    def validate(self):
        raise NotImplementedError('Must be implemented in subclass')
