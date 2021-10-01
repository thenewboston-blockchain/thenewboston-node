from urllib.parse import urlencode

from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.tests.base import as_primary_validator, force_blockchain

API_V1_LIST_NODES_URL = '/api/v1/nodes/'


def test_can_list_nodes(
    api_client, file_blockchain, primary_validator_key_pair, another_node_key_pair, another_node_network_address
):
    blockchain = file_blockchain

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[another_node_network_address], fee_amount=3, signing_key=another_node_key_pair.private
    )
    blockchain.add_block(
        Block.create_from_signed_change_request(blockchain, request, primary_validator_key_pair.private)
    )

    with force_blockchain(blockchain), as_primary_validator():
        response = api_client.get(API_V1_LIST_NODES_URL)

    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 3
    assert len(data['results']) == 3
    # TODO(dmu) HIGH: Add response content validation


def test_can_list_nodes_w_offset(
    api_client, file_blockchain, primary_validator_key_pair, another_node_key_pair, another_node_network_address
):
    blockchain = file_blockchain

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[another_node_network_address], fee_amount=3, signing_key=another_node_key_pair.private
    )
    blockchain.add_block(
        Block.create_from_signed_change_request(blockchain, request, primary_validator_key_pair.private)
    )

    with force_blockchain(blockchain), as_primary_validator():
        params = urlencode({'limit': 1, 'offset': '1'})
        response = api_client.get(API_V1_LIST_NODES_URL + '?' + params)

    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 3
    assert len(data['results']) == 1
    # TODO(dmu) HIGH: Add response content validation
