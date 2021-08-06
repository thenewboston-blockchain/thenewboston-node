import pytest

from thenewboston_node.business_logic.models.node import Node


@pytest.fixture
def pv_fee_amount():
    return 4


@pytest.fixture
def primary_validator(primary_validator_key_pair, pv_fee_amount):
    return Node(identifier=primary_validator_key_pair.public, network_addresses=['http://localhost'], fee_amount=4)


@pytest.fixture
def preferred_node(node_key_pair):
    return Node(identifier=node_key_pair.public, network_addresses=['http://pref.localhost'], fee_amount=1)
