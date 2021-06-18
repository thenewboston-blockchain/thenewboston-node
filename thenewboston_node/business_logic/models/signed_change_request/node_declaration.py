import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from thenewboston_node.core.utils.types import hexstr

from ..signed_change_request_message import NodeDeclarationSignedChangeRequestMessage
from .base import SignedChangeRequest

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='NodeDeclarationSignedChangeRequest')


@dataclass
class NodeDeclarationSignedChangeRequest(SignedChangeRequest):
    message: NodeDeclarationSignedChangeRequestMessage

    @classmethod
    def create(
        cls: Type[T],
        *,
        identifier: hexstr,
        network_addresses: list[str],
        fee_amount: int,
        signing_key: hexstr,
        fee_account: Optional[hexstr] = None
    ) -> T:
        message = NodeDeclarationSignedChangeRequestMessage.create(
            identifier=identifier,
            network_addresses=network_addresses,
            fee_amount=fee_amount,
            fee_account=fee_account,
        )
        return cls.create_from_signed_change_request_message(message, signing_key)

    def validate(self, blockchain, block_number: Optional[int] = None):
        # TODO(dmu) CRIRICAL: Implement
        return
