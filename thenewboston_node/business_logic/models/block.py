from dataclasses import dataclass

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.node import get_signing_key
from thenewboston_node.core.utils.cryptography import generate_verify_key
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .block_message import BlockMessage
from .transfer_request import TransferRequest


@fake_super_methods
@dataclass_json
@dataclass
class Block:
    node_identifier: str
    message: BlockMessage
    message_hash: str
    message_signature: str

    @classmethod
    def from_transfer_request(cls, transfer_request: TransferRequest):
        message = BlockMessage.from_transfer_request(transfer_request)

        # TODO(dmu) LOW: Consider caching signing and verify keys
        signing_key = get_signing_key()
        return Block(
            node_identifier=generate_verify_key(signing_key),
            message=message,
            message_hash=message.get_hash(),
            message_signature=message.generate_signature(signing_key)
        )

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['message'] = self.message.to_dict()
        return dict_
