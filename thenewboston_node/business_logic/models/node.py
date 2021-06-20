from dataclasses import dataclass, field
from typing import Optional

from thenewboston_node.business_logic.enums import NodeType
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from .base import BaseDataclass


@revert_docstring
@dataclass
@cover_docstring
class Node(BaseDataclass):
    identifier: hexstr = field(
        metadata={'example_value': '657cf373f6f8fb72854bd302269b8b2b3576e3e2a686bd7d0a112babaa1790c6'}
    )
    network_addresses: list[str] = field(metadata={'example_value': ['https://pv-non-existing.thenewboston.com:8000']})
    fee_amount: int = field(metadata={'example_value': 4})
    fee_account: Optional[hexstr] = field(
        default=None, metadata={'example_value': '7a5dc06babda703a7d2d8ea18d3309a0c5e6830a25bac03e69633d283244e001'}
    )

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
