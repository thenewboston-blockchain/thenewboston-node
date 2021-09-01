from rest_framework import status

from thenewboston_node.business_logic.tests.base import force_blockchain

API_V1_LIST_BLOCKCHAIN_STATE_URL = '/api/v1/blockchain-states-meta/'


def test_memory_blockchain_supported(api_client, memory_blockchain):
    with force_blockchain(memory_blockchain):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    assert response.status_code == status.HTTP_200_OK


def test_can_list_blockchain_state_meta(api_client, file_blockchain_with_two_blockchain_states):

    with force_blockchain(file_blockchain_with_two_blockchain_states):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 2

    blockchain_state_0, blockchain_state_1 = data['results']
    expected = file_blockchain_with_two_blockchain_states.get_first_blockchain_state().last_block_number
    assert blockchain_state_0['last_block_number'] == expected
    assert blockchain_state_0['url_path'] == (
        '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/0000000000000000000!-blockchain-state.msgpack'
    )
    assert len(blockchain_state_0['urls']) == 1
    assert blockchain_state_0['urls'][0] == (
        'http://localhost:8555/blockchain/blockchain-states'
        '/0/0/0/0/0/0/0/0/0000000000000000000!-blockchain-state.msgpack'
    )

    assert blockchain_state_1['last_block_number'] == 1
    assert blockchain_state_1['url_path'] == (
        '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/00000000000000000001-blockchain-state.msgpack'
    )
    assert len(blockchain_state_1['urls']) == 1
    assert blockchain_state_1['urls'][0] == (
        'http://localhost:8555/blockchain/blockchain-states'
        '/0/0/0/0/0/0/0/0/00000000000000000001-blockchain-state.msgpack'
    )


def test_can_sort_ascending_blockchain_states_meta(api_client, file_blockchain_with_two_blockchain_states):
    with force_blockchain(file_blockchain_with_two_blockchain_states):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=last_block_number')

    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 2

    blockchain_state_0, blockchain_state_1 = data['results']
    expected = file_blockchain_with_two_blockchain_states.get_first_blockchain_state().last_block_number
    assert blockchain_state_0['last_block_number'] == expected
    assert blockchain_state_1['last_block_number'] == 1


def test_can_sort_descending_blockchain_states_meta(api_client, file_blockchain_with_two_blockchain_states):
    with force_blockchain(file_blockchain_with_two_blockchain_states):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=-last_block_number')

    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 2

    blockchain_state_0, blockchain_state_1 = data['results']
    assert blockchain_state_0['last_block_number'] == 1
    expected = file_blockchain_with_two_blockchain_states.get_first_blockchain_state().last_block_number
    assert blockchain_state_1['last_block_number'] == expected


def test_can_get_blockchain_states_meta_w_limit(api_client, file_blockchain_with_two_blockchain_states):
    with force_blockchain(file_blockchain_with_two_blockchain_states):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?limit=1')

    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1

    expected = file_blockchain_with_two_blockchain_states.get_first_blockchain_state().last_block_number
    assert data['results'][0]['last_block_number'] == expected


def test_can_get_blockchain_states_meta_w_offset(api_client, file_blockchain_with_two_blockchain_states):
    with force_blockchain(file_blockchain_with_two_blockchain_states):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?limit=1&offset=1')

    assert response.status_code == 200
    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert data['results'][0]['last_block_number'] == 1


def test_pagination_is_applied_after_ordering(api_client, file_blockchain_with_two_blockchain_states):
    with force_blockchain(file_blockchain_with_two_blockchain_states):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?offset=1&ordering=-last_block_number')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['count'] == 2
    assert len(data['results']) == 1
    assert data['results'][0]['last_block_number'] == -1
