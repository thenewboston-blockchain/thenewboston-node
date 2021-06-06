from dataclasses import dataclass
from typing import Optional

from thenewboston_node.core.utils.types import hexstr

from ..node import Node
from .base import SignedChangeRequestMessage


@dataclass
class NodeDeclarationSignedChangeRequestMessage(SignedChangeRequestMessage):
    """Network address registration signed change request message"""

    node: Node

    @classmethod
    def create(
        cls, identifier: hexstr, network_addresses: list[str], fee_amount: int, fee_account: Optional[hexstr] = None
    ):
        return cls(
            node=Node(
                identifier=identifier,
                network_addresses=network_addresses,
                fee_amount=fee_amount,
                fee_account=fee_account,
            )
        )
