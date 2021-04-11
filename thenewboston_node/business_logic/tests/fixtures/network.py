from unittest.mock import patch

from django.test import override_settings

import pytest

from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode
from thenewboston_node.business_logic.network.mock_network import MockNetwork


@pytest.fixture
def primary_validator(primary_validator_key_pair):
    return PrimaryValidator(identifier=primary_validator_key_pair.public, fee_amount=4)


@pytest.fixture
def get_primary_validator_mock(primary_validator):
    with patch.object(MockNetwork, 'get_primary_validator', return_value=primary_validator) as mock:
        yield mock


@pytest.fixture
def preferred_node(node_key_pair):
    return RegularNode(identifier=node_key_pair.public, fee_amount=1)


@pytest.fixture
def get_preferred_node_mock(preferred_node):
    with patch.object(MockNetwork, 'get_preferred_node', return_value=preferred_node) as mock:
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
