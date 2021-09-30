import pytest

from thenewboston_node.business_logic.models.node import Node
from thenewboston_node.business_logic.tests.baker_factories import baker


@pytest.fixture
def pv_network_address():
    return 'http://pv.non-existing-domain:8555/'


@pytest.fixture
def pv_fee_amount():
    return 4


@pytest.fixture
def primary_validator(primary_validator_key_pair, pv_network_address, pv_fee_amount):
    pv = baker.make(
        Node,
        identifier=primary_validator_key_pair.public,
        network_addresses=[pv_network_address],
        fee_amount=pv_fee_amount,
        fee_account=None,
    )
    pv._test_key_pair = primary_validator_key_pair
    return pv


@pytest.fixture
def cv_network_address():
    return 'http://cv.non-existing-domain:8555/'


@pytest.fixture
def cv_fee_amount():
    return 1


@pytest.fixture
def confirmation_validator(confirmation_validator_key_pair, cv_network_address, cv_fee_amount):
    pv = baker.make(
        Node,
        identifier=confirmation_validator_key_pair.public,
        network_addresses=[cv_network_address],
        fee_amount=cv_fee_amount,
        fee_account=None,
    )
    pv._test_key_pair = confirmation_validator_key_pair
    return pv


@pytest.fixture
def preferred_node_network_address():
    return 'http://preferred-node.non-existing-domain:8555/'


@pytest.fixture
def preferred_node_fee_amount():
    return 1


@pytest.fixture
def preferred_node(preferred_node_key_pair, preferred_node_network_address, preferred_node_fee_amount):
    return baker.make(
        Node,
        identifier=preferred_node_key_pair.public,
        network_addresses=[preferred_node_network_address],
        fee_amount=preferred_node_fee_amount,
        fee_account=None
    )


@pytest.fixture
def another_node_network_address():
    return 'http://another-node.non-existing-domain:8555/'


@pytest.fixture
def another_node(another_node_key_pair, another_node_network_address):
    return baker.make(
        Node,
        identifier=another_node_key_pair.public,
        network_addresses=[another_node_network_address],
        fee_amount=1,
        fee_account=None
    )
