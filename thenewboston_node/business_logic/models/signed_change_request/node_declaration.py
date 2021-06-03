import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.core.utils.dataclass import fake_super_methods

from ..signed_change_request_message import NodeDeclarationSignedChangeRequestMessage
from .base import SignedChangeRequest

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='NodeDeclarationSignedChangeRequest')


@fake_super_methods
@dataclass_json
@dataclass
class NodeDeclarationSignedChangeRequest(SignedChangeRequest):
    message: NodeDeclarationSignedChangeRequestMessage
    """Network address registration request payload"""

    @classmethod
    def create(cls: Type[T], network_addresses: list[str], signing_key: str) -> T:
        message = NodeDeclarationSignedChangeRequestMessage.create(network_addresses)
        return cls.create_from_signed_change_request_message(message, signing_key)

    def validate(self, blockchain, block_number: Optional[int] = None):
        return
