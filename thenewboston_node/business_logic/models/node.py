from dataclasses import dataclass
from typing import Optional

from thenewboston_node.business_logic.enums import NodeType
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from .base import BaseDataclass


@revert_docstring
@dataclass
@cover_docstring
class Node(BaseDataclass):
    identifier: hexstr
    network_addresses: list[str]
    fee_amount: int
    fee_account: Optional[hexstr] = None

    def serialize_to_dict(self, skip_none_values=True, coerce_to_json_types=True, exclude=('identifier',)):
        return super(Node, self).serialize_to_dict(
            skip_none_values=skip_none_values,
            coerce_to_json_types=coerce_to_json_types,
            exclude=exclude,
        )


# TODO(dmu) HIGH: Do we really need `PrimaryValidator` and `RegularNode` classes?
@dataclass
class PrimaryValidator(Node):

    @property
    def node_type(self):
        return NodeType.PRIMARY_VALIDATOR.value


@dataclass
class RegularNode(Node):

    @property
    def node_type(self):
        return NodeType.REGULAR_NODE.value
