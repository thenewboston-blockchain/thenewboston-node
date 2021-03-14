import logging
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.node import get_signing_key
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .base import SignableMixin
from .block_message import BlockMessage
from .transfer_request import TransferRequest

T = TypeVar('T', bound='Block')

logger = logging.getLogger(__name__)


@fake_super_methods
@dataclass_json
@dataclass
class Block(SignableMixin):
    verify_key_field_name = 'node_identifier'

    message: BlockMessage
    node_identifier: Optional[str] = None
    message_hash: Optional[str] = None
    message_signature: Optional[str] = None

    @classmethod
    def from_transfer_request(cls: Type[T], transfer_request: TransferRequest) -> T:
        message = BlockMessage.from_transfer_request(transfer_request)
        block = cls(message=message)

        signing_key = get_signing_key()
        block.sign(signing_key)
        block.hash_message()
        return block

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['message'] = self.message.to_dict()
        return dict_

    def hash_message(self) -> None:
        message_hash = self.message.get_hash()
        stored_message_hash = self.message_hash
        if stored_message_hash and stored_message_hash != message_hash:
            logger.warning('Overwriting existing message hash')

        self.message_hash = message_hash

    def is_valid(self) -> bool:
        raise NotImplementedError()
