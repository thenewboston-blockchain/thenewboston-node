from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .block_message import BlockMessage


@dataclass_json
@dataclass
class Block:
    message: BlockMessage
    node_identifier: str
    signature: str
