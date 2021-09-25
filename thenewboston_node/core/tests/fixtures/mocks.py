import json
from unittest.mock import patch
from urllib.parse import urljoin

import httpretty
import pytest


@pytest.fixture(autouse=True)
def outer_web_mock():
    """
    This mock should prevent any accidental access to outer services during
    test runs
    """

    httpretty.enable(verbose=True, allow_net_connect=False)
    yield httpretty
    httpretty.disable()
    httpretty.reset()


@pytest.fixture
def node_mock(outer_web_mock, blockchain_state_meta, another_node_network_address):
    outer_web_mock.register_uri(
        outer_web_mock.GET,
        urljoin(another_node_network_address, 'api/v1/blockchain-states-meta/'),
        body=json.dumps({
            'count': 1,
            'results': [blockchain_state_meta],
        }),
    )
    yield outer_web_mock


@pytest.fixture
def node_mock_for_node_client(client):
    with patch('thenewboston_node.core.clients.node.requests_get',
               new=client.get), patch('thenewboston_node.core.clients.node.requests_post', new=client.post):
        yield
