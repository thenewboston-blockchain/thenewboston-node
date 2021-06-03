from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from thenewboston_node.business_logic.enums import NodeType


@dataclass_json
@dataclass
class Node:
    identifier: str
    """Identifier"""

    fee_amount: int
    """Fee amount"""

    node_type: str
    """Node type"""

    fee_account: Optional[str] = None
    """Fee account"""


@dataclass_json
@dataclass
class PrimaryValidator(Node):
    node_type: str = NodeType.PRIMARY_VALIDATOR.value


@dataclass_json
@dataclass
class RegularNode(Node):
    node_type: str = NodeType.REGULAR_NODE.value
