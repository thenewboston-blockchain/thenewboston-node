import logging
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Type, TypeVar

from thenewboston_node.business_logic.models.constants import BlockType
from thenewboston_node.core.utils.cryptography import derive_public_key
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from ..account_state import AccountState
from ..signed_change_request_message import NodeDeclarationSignedChangeRequestMessage
from .base import SignedChangeRequest

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='NodeDeclarationSignedChangeRequest')


@revert_docstring
@dataclass
@cover_docstring
class NodeDeclarationSignedChangeRequest(SignedChangeRequest):
    block_type: ClassVar[str] = BlockType.NODE_DECLARATION.value

    message: NodeDeclarationSignedChangeRequestMessage

    @classmethod
    def create(
        cls: Type[T],
        *,
        network_addresses: list[str],
        fee_amount: int,
        signing_key: hexstr,
        fee_account: Optional[hexstr] = None
    ) -> T:
        message = NodeDeclarationSignedChangeRequestMessage.create(
            identifier=derive_public_key(signing_key),
            network_addresses=network_addresses,
            fee_amount=fee_amount,
            fee_account=fee_account,
        )
        return cls.create_from_signed_change_request_message(message, signing_key)

    @classmethod
    def create_from_node(cls, node, signing_key):
        assert node.identifier == derive_public_key(signing_key)
        message = NodeDeclarationSignedChangeRequestMessage(node=node)
        return cls.create_from_signed_change_request_message(message, signing_key)

    @classmethod
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, override: Optional[dict[str, Any]] = None):
        override = override or {}
        message = dict_.get('message')
        if isinstance(message, dict) and 'message' not in override:
            node = message.get('node')
            if isinstance(node, dict):
                node['identifier'] = dict_.get('signer')

        return super().deserialize_from_dict(
            dict_=dict_, complain_excessive_keys=complain_excessive_keys, override=override
        )

    def serialize_to_dict(self, skip_none_values=True, coerce_to_json_types=True, exclude=()):
        serialized = super().serialize_to_dict(
            skip_none_values=skip_none_values, coerce_to_json_types=coerce_to_json_types, exclude=exclude
        )
        serialized['message']['node'].pop('identifier', None)
        return serialized

    def get_updated_account_states(self, blockchain) -> dict[hexstr, AccountState]:
        return {self.signer: AccountState(node=deepcopy(self.message.node))}
