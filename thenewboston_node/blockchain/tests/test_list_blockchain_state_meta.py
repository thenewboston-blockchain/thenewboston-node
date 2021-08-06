from rest_framework import status

API_V1_LIST_BLOCKCHAIN_STATE_URL = '/api/v1/blockchain-states-meta/'


def test_only_file_blockchain_supported(api_client, forced_memory_blockchain):
    response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
    assert response.json() == {'detail': 'Not implemented.'}


def test_can_list_blockchain_state_meta(api_client, declared_node_file_blockchain, blockchain_genesis_state):
    response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 2

    blockchain_state_0, blockchain_state_1 = data['results']
    assert blockchain_state_0['last_block_number'] == blockchain_genesis_state.last_block_number
    assert blockchain_state_0['url_path'] == (
        '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack'
    )
    assert len(blockchain_state_0['urls']) == 1
    assert blockchain_state_0['urls'][0] == (
        'http://localhost/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack'
    )

    assert blockchain_state_1['last_block_number'] == 0
    assert blockchain_state_1['url_path'] == (
        '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/0000000000-blockchain-state.msgpack'
    )
    assert len(blockchain_state_1['urls']) == 1
    assert blockchain_state_1['urls'][0] == (
        'http://localhost/blockchain/blockchain-states/0/0/0/0/0/0/0/0/0000000000-blockchain-state.msgpack'
    )


def test_can_sort_ascending_blockchain_states_meta(
    api_client, declared_node_file_blockchain, blockchain_genesis_state
):
    response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=asc')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 2

    blockchain_state_0, blockchain_state_1 = data['results']
    assert blockchain_state_0['last_block_number'] == blockchain_genesis_state.last_block_number
    assert blockchain_state_1['last_block_number'] == 0


def test_can_sort_descending_blockchain_states_meta(
    api_client, declared_node_file_blockchain, blockchain_genesis_state
):
    response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=desc')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 2

    blockchain_state_0, blockchain_state_1 = data['results']
    assert blockchain_state_0['last_block_number'] == 0
    assert blockchain_state_1['last_block_number'] == blockchain_genesis_state.last_block_number


def test_blockchain_states_meta_ordering_is_validated(api_client, declared_node_file_blockchain):
    response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=1')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_can_get_blockchain_states_meta_w_limit(api_client, declared_node_file_blockchain, blockchain_genesis_state):
    response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?limit=1')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert data['results'][0]['last_block_number'] == blockchain_genesis_state.last_block_number
    assert data['previous'] is None
    assert data['next'].endswith(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?limit=1&offset=1')


def test_can_get_blockchain_states_meta_w_offset(api_client, declared_node_file_blockchain, blockchain_genesis_state):
    response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?limit=1&offset=1')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert data['results'][0]['last_block_number'] == 0
    assert data['next'] is None
    assert data['previous'].endswith(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?limit=1')
