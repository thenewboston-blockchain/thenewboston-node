from urllib.parse import urlencode

import pytest

from thenewboston_node.business_logic.tests.base import as_primary_validator, force_blockchain

API_V1_LIST_BLOCKCHAIN_STATE_URL = '/api/v1/block-chunks-meta/'


def test_can_list_block_chunk_meta(api_client, file_blockchain_with_three_block_chunks, pv_network_address):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain), as_primary_validator():
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['results']) == 3

    meta_0, meta_1, meta_2 = response_json['results']
    assert meta_0 == {
        'start_block_number':
            0,
        'end_block_number':
            2,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ]
    }
    assert meta_1 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ]
    }
    assert meta_2 == {
        'start_block_number':
            6,
        'end_block_number':
            7,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }


def test_can_order_block_chunk_meta(api_client, file_blockchain_with_three_block_chunks, pv_network_address):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain), as_primary_validator():
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=-start_block_number')

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['results']) == 3

    meta_0, meta_1, meta_2 = response_json['results']
    assert meta_2 == {
        'start_block_number':
            0,
        'end_block_number':
            2,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ]
    }
    assert meta_1 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ]
    }
    assert meta_0 == {
        'start_block_number':
            6,
        'end_block_number':
            7,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }


def test_can_order_block_chunk_meta_with_limit(
    api_client, file_blockchain_with_three_block_chunks, pv_network_address
):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain), as_primary_validator():
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=-start_block_number&limit=2')

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['results']) == 2

    meta_0, meta_1 = response_json['results']
    assert meta_1 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ]
    }
    assert meta_0 == {
        'start_block_number':
            6,
        'end_block_number':
            7,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }


def test_can_order_block_chunk_meta_with_limit_and_offset(
    api_client, file_blockchain_with_three_block_chunks, pv_network_address
):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain), as_primary_validator():
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=-start_block_number&limit=1&offset=1')

    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json['results']) == 1
    (meta_0,) = response_json['results']
    assert meta_0 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ]
    }


@pytest.mark.parametrize(
    'from_block_number,to_block_number,block_chunk_map', (
        (0, None, {
            0: 0,
            1: 1,
            2: 2
        }),
        (1, None, {
            0: 0,
            1: 1,
            2: 2
        }),
        (2, None, {
            0: 0,
            1: 1,
            2: 2
        }),
        (3, None, {
            0: 1,
            1: 2
        }),
        (4, None, {
            0: 1,
            1: 2
        }),
        (5, None, {
            0: 1,
            1: 2
        }),
        (6, None, {
            0: 2
        }),
        (7, None, {
            0: 2
        }),
        (8, None, {}),
        (None, 10, {
            0: 0,
            1: 1,
            2: 2
        }),
        (None, 9, {
            0: 0,
            1: 1,
            2: 2
        }),
        (None, 8, {
            0: 0,
            1: 1,
            2: 2
        }),
        (None, 7, {
            0: 0,
            1: 1,
            2: 2
        }),
        (None, 6, {
            0: 0,
            1: 1,
            2: 2
        }),
        (None, 5, {
            0: 0,
            1: 1
        }),
        (None, 4, {
            0: 0,
            1: 1
        }),
        (None, 3, {
            0: 0,
            1: 1
        }),
        (None, 2, {
            0: 0
        }),
        (None, 1, {
            0: 0
        }),
        (None, 0, {
            0: 0
        }),
        (0, 10, {
            0: 0,
            1: 1,
            2: 2
        }),
        (0, 9, {
            0: 0,
            1: 1,
            2: 2
        }),
        (0, 8, {
            0: 0,
            1: 1,
            2: 2
        }),
        (0, 7, {
            0: 0,
            1: 1,
            2: 2
        }),
        (0, 6, {
            0: 0,
            1: 1,
            2: 2
        }),
        (0, 5, {
            0: 0,
            1: 1
        }),
        (1, 5, {
            0: 0,
            1: 1
        }),
        (2, 5, {
            0: 0,
            1: 1
        }),
        (3, 5, {
            0: 1
        }),
        (4, 5, {
            0: 1
        }),
        (5, 5, {
            0: 1
        }),
    )
)
def test_filter_by_block_number_range(
    api_client, file_blockchain_with_three_block_chunks, from_block_number, to_block_number, block_chunk_map
):
    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain), as_primary_validator():
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    assert response.status_code == 200
    response_json = response.json()
    block_chunks = response_json['results']
    assert len(block_chunks) == 3
    assert block_chunks[0]['start_block_number'] == 0 and block_chunks[0]['end_block_number'] == 2
    assert block_chunks[1]['start_block_number'] == 3 and block_chunks[1]['end_block_number'] == 5
    assert block_chunks[2]['start_block_number'] == 6 and block_chunks[2]['end_block_number'] == 7

    query_parameters = {}
    if from_block_number is not None:
        query_parameters['from_block_number'] = from_block_number
    if to_block_number is not None:
        query_parameters['to_block_number'] = to_block_number

    with force_blockchain(blockchain), as_primary_validator():
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?' + urlencode(query_parameters))

    assert response.status_code == 200
    response_json = response.json()
    filtered_block_chunks = response_json['results']
    assert len(filtered_block_chunks) == len(block_chunk_map)
    for filtered_index, original_index in block_chunk_map.items():
        assert block_chunks[original_index] == filtered_block_chunks[filtered_index]
