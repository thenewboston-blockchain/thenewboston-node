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
