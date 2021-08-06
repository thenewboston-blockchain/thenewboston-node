import pytest

from thenewboston_node.business_logic.models.node import RegularNode
from thenewboston_node.business_logic.utils.network import make_own_node


@pytest.fixture
def node_fee_amount():
    return 3


@pytest.fixture
def primary_validator(primary_validator_key_pair, node_fee_amount):
    return make_own_node(
        identifier=primary_validator_key_pair.public,
        network_addresses=['http://localhost'],
        fee_amount=node_fee_amount
    )


@pytest.fixture
def preferred_node(node_key_pair):
    return RegularNode(identifier=node_key_pair.public, network_addresses=['http://pref.localhost'], fee_amount=1)
