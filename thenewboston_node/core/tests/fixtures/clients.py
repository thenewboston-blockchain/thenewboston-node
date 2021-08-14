import pytest
from rest_framework.test import APIClient

from thenewboston_node.core.clients.node import NodeClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def node_client():
    return NodeClient.get_instance()
