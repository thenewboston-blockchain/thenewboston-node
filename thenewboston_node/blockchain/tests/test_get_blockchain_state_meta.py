import pytest
from rest_framework import status

API_V1_BLOCKCHAIN_STATE_URL_PATTERN = '/api/v1/blockchain-states-meta/{block_number}/'


@pytest.mark.parametrize('block_number', ('invalid_id', -2))
def test_invalid_block_number_returns_400(api_client, declared_node_file_blockchain, block_number):
    response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=block_number))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_can_get_blockchain_genesis_state_meta(api_client, declared_node_file_blockchain, blockchain_genesis_state):
    response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=-1))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data['last_block_number'] == blockchain_genesis_state.last_block_number
    assert data['url_path'] == '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack'
    assert len(data['urls']) == 1
    assert data['urls'][0] == (
        'http://localhost/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack'
    )


def test_can_get_last_blockchain_state_meta(api_client, declared_node_file_blockchain):
    response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=999))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data['last_block_number'] == 0


def test_blockchain_state_meta_block_number_is_noninclusive(
    api_client, declared_node_file_blockchain, blockchain_genesis_state
):
    response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=0))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data['last_block_number'] == blockchain_genesis_state.last_block_number


def test_blockchain_state_meta_urls_returns_500_if_node_undeclared(
    api_client, forced_file_blockchain, blockchain_genesis_state
):
    response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=-1))

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()

    assert data['detail'] == 'Requested node is unregistered in the blockchain'
