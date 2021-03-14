from unittest.mock import patch

from django.test import override_settings

import pytest

from thenewboston_node.business_logic.enums import NodeType
from thenewboston_node.business_logic.models.node import Node, PrimaryValidator
from thenewboston_node.business_logic.network.mock_network import MockNetwork


@pytest.fixture
def get_primary_validator_mock(primary_validator_key_pair):
    return_value = PrimaryValidator(identifier=primary_validator_key_pair.public, fee_amount=4)
    with patch.object(MockNetwork, 'get_primary_validator', return_value=return_value) as mock:
        yield mock


@pytest.fixture
def get_preferred_node_mock(node_key_pair):
    return_value = Node(identifier=node_key_pair.public, fee_amount=1, type_=NodeType.NODE.value)
    with patch.object(MockNetwork, 'get_preferred_node', return_value=return_value) as mock:
        yield mock


@pytest.fixture
def forced_mock_network():
    network_settings = {
        'class': 'thenewboston_node.business_logic.network.mock_network.MockNetwork',
    }

    MockNetwork.clear_instance_cache()
    with override_settings(NETWORK=network_settings):
        yield MockNetwork.get_instance()
    MockNetwork.clear_instance_cache()
