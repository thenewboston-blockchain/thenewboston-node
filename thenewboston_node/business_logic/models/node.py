from dataclasses import dataclass, field
from typing import Optional

from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.validators import (
    validate_gte_value, validate_hexadecimal, validate_network_address, validate_not_empty, validate_not_none,
    validate_type
)
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from .base import BaseDataclass


@revert_docstring
@dataclass
@cover_docstring
class Node(BaseDataclass):
    network_addresses: list[str] = field(metadata={'example_value': ['https://pv-non-existing.thenewboston.com:8000']})
    fee_amount: int = field(metadata={'example_value': 4})

    # We need identifier to be optional for deserialization purposes
    identifier: Optional[hexstr] = field(
        default=None, metadata={'example_value': '657cf373f6f8fb72854bd302269b8b2b3576e3e2a686bd7d0a112babaa1790c6'}
    )
    fee_account: Optional[hexstr] = field(
        default=None, metadata={'example_value': '7a5dc06babda703a7d2d8ea18d3309a0c5e6830a25bac03e69633d283244e001'}
    )

    def serialize_to_dict(self, skip_none_values=True, coerce_to_json_types=True, exclude=()):
        serialized = super().serialize_to_dict(
            skip_none_values=skip_none_values, coerce_to_json_types=coerce_to_json_types, exclude=exclude
        )
        fee_account = serialized.get('fee_account')
        if fee_account is not None and fee_account == serialized['identifier']:
            del serialized['fee_account']

        return serialized

    def __hash__(self):
        return hash(self.identifier)

    def validate(self):
        self.validate_identifier()
        self.validate_fee_amount()
        self.validate_fee_account()
        self.validate_network_addresses()

    def validate_identifier(self):
        validate_not_empty(f'{self.humanized_class_name} identifier', self.identifier)
        validate_type(f'{self.humanized_class_name} identifier', self.identifier, str)
        validate_hexadecimal(f'{self.humanized_class_name} identifier', self.identifier)

    def validate_network_addresses(self):
        for network_address in self.network_addresses:
            validate_not_empty(f'{self.humanized_class_name} network_addresses', network_address)
            validate_network_address(f'{self.humanized_class_name} network_addresses', network_address)

    def validate_fee_amount(self):
        validate_not_none(f'{self.humanized_class_name} fee_amount', self.fee_amount)
        validate_type(f'{self.humanized_class_name} fee_amount', self.fee_amount, int)
        validate_gte_value(f'{self.humanized_class_name} fee_amount', self.fee_amount, 0)

    def validate_fee_account(self):
        if self.fee_account is not None:
            validate_type(f'{self.humanized_class_name} fee_account', self.fee_account, str)
            validate_hexadecimal(f'{self.humanized_class_name} fee_account', self.fee_account)


# TODO(dmu) HIGH: Do we really need `PrimaryValidator` and `RegularNode` classes?
@dataclass
class PrimaryValidator(Node):

    @property
    def node_type(self):
        return NodeRole.PRIMARY_VALIDATOR.value


@dataclass
class RegularNode(Node):

    @property
    def node_type(self):
        return NodeRole.REGULAR_NODE.value
