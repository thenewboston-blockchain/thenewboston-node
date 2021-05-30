from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .base import SignedChangeRequestMessage


@dataclass_json
@dataclass
class NodeDeclarationSignedChangeRequestMessage(SignedChangeRequestMessage):
    """Network address registration signed change request message"""

    network_addresses: list[str]
    """Network addressess"""

    @classmethod
    def create(cls, network_addresses: list[str]):
        return cls(network_addresses=network_addresses)
