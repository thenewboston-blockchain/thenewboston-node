import json
import re

import httpretty


@httpretty.activate(verbose=True, allow_net_connect=False)
def test_get_latest_blockchain_state_meta_by_network_address(node_client):
    network_address = 'http://127.0.0.1:8555'

    state_meta = {
        'last_block_number':
            None,
        'url_path':
            '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack',
        'urls': [
            'http://77.105.174.247:8555/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack'
        ],
    }
    httpretty.register_uri(
        httpretty.GET,
        re.compile(f'{network_address}/.*'),
        body=json.dumps({
            'count': 1,
            'results': [state_meta],
        }),
    )

    result = node_client.get_latest_blockchain_state_meta_by_network_address(network_address)
    assert result == state_meta
