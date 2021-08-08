import pytest
from rest_framework import status

from thenewboston_node.business_logic.tests.base import force_blockchain

API_V1_BLOCKCHAIN_STATE_URL_PATTERN = '/api/v1/blockchain-states-meta/{block_number}/'


@pytest.mark.parametrize('block_number', (-2,))
def test_invalid_block_number_returns_400(api_client, file_blockchain, block_number):
    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=block_number))

    assert response.status_code == 400


def test_can_get_blockchain_genesis_state_meta(api_client, file_blockchain, blockchain_genesis_state):
    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=-1))

    assert response.status_code == 200
    response_json = response.json()

    assert response_json == {
        'last_block_number':
            blockchain_genesis_state.last_block_number,
        'url_path':
            '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack',
        'urls': [
            'http://localhost:8555/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack'
        ]
    }


def test_can_get_last_blockchain_state_meta(api_client, file_blockchain):
    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=999))

    # TODO(dmu) HIGH: Respond with 404
    assert response.status_code == 200
    data = response.json()

    assert data['last_block_number'] is None


def test_blockchain_state_meta_block_number_is_noninclusive(api_client, file_blockchain, blockchain_genesis_state):
    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=0))

    # TODO(dmu) HIGH: Respond with 404
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data['last_block_number'] == blockchain_genesis_state.last_block_number


# def test_blockchain_state_meta_urls_returns_500_if_node_undeclared(
#     api_client, file_blockchain,
# ):
#     with force_blockchain(file_blockchain):
#         response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=-1))
#
#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#     data = response.json()
#
#     assert data['detail'] == 'Requested node is unregistered in the blockchain'
