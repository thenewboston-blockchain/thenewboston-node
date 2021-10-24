from unittest.mock import patch
from urllib.parse import urljoin

import pytest


@pytest.fixture
def blockchain_state_meta(another_node_network_address):
    return {
        'last_block_number':
            None,
        'url_path':
            '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack',
        'urls': [
            urljoin(
                another_node_network_address,
                'blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack'
            )
        ],
    }


@pytest.fixture
def start_send_block_confirmations_mock():
    with patch('thenewboston_node.blockchain.serializers.block.start_send_block_confirmations') as mock:
        yield mock


@pytest.fixture
def start_send_block_confirmation_mock():
    with patch('thenewboston_node.blockchain.tasks.block_confirmation.start_send_block_confirmation') as mock:
        yield mock
