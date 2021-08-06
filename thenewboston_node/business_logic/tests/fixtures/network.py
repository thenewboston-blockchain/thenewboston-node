import pytest

from thenewboston_node.business_logic.models.node import RegularNode
from thenewboston_node.business_logic.utils.network import make_own_node


@pytest.fixture
def primary_validator(primary_validator_key_pair):
    return make_own_node(identifier=primary_validator_key_pair.public, network_addresses=['http://localhost'])


@pytest.fixture
def preferred_node(node_key_pair):
    return RegularNode(identifier=node_key_pair.public, network_addresses=['http://pref.localhost'], fee_amount=1)
