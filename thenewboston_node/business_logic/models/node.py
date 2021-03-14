from dataclasses import dataclass

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.enums import NodeType


@dataclass_json
@dataclass
class Node:
    identifier: str
    fee_amount: int
    type_: str


@dataclass_json
@dataclass
class PrimaryValidator(Node):
    type_: str = NodeType.PRIMARY_VALIDATOR.value
