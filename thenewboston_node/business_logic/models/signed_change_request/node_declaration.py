import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from ..signed_change_request_message import NodeDeclarationSignedChangeRequestMessage
from .base import SignedChangeRequest

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='NodeDeclarationSignedChangeRequest')


@dataclass
class NodeDeclarationSignedChangeRequest(SignedChangeRequest):
    message: NodeDeclarationSignedChangeRequestMessage
    """Network address registration request payload"""

    @classmethod
    def create(
        cls: Type[T],
        *,
        network_addresses: list[str],
        fee_amount: int,
        signing_key: str,
        fee_account: Optional[str] = None
    ) -> T:
        message = NodeDeclarationSignedChangeRequestMessage.create(
            network_addresses=network_addresses,
            fee_amount=fee_amount,
            fee_account=fee_account,
        )
        return cls.create_from_signed_change_request_message(message, signing_key)

    def validate(self, blockchain, block_number: Optional[int] = None):
        return
