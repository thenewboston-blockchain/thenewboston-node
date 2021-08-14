import pytest

from thenewboston_node.business_logic.models.node import Node
from thenewboston_node.business_logic.tests.baker_factories import baker


@pytest.fixture
def pv_fee_amount():
    return 4


@pytest.fixture
def primary_validator(primary_validator_key_pair, pv_fee_amount):
    return baker.make(
        Node,
        identifier=primary_validator_key_pair.public,
        network_addresses=['http://localhost:8555/'],
        fee_amount=4,
        fee_account=None,
    )


@pytest.fixture
def preferred_node(preferred_node_key_pair):
    return baker.make(
        Node,
        identifier=preferred_node_key_pair.public,
        network_addresses=['http://pref.localhost:8555/'],
        fee_amount=1,
        fee_account=None
    )


@pytest.fixture
def another_node(another_node_key_pair):
    return baker.make(
        Node,
        identifier=another_node_key_pair.public,
        network_addresses=['http://another.localhost:8555/'],
        fee_amount=1,
        fee_account=None
    )


@pytest.fixture
def another_node_network_address(another_node):
    network_addresses = another_node.network_addresses
    assert network_addresses
    return network_addresses[0]
