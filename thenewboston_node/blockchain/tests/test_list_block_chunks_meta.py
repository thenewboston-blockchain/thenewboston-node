# from rest_framework import status

from thenewboston_node.business_logic.tests.base import force_blockchain

API_V1_LIST_BLOCKCHAIN_STATE_URL = '/api/v1/block-chunks-meta/'


def test_can_list_block_chunk_meta(api_client, file_blockchain_with_three_block_chunks):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['count'] == 3

    meta_0, meta_1, meta_2 = response_json['results']
    assert meta_0 == {
        'start_block_number':
            0,
        'end_block_number':
            2,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
        ),
        'urls': [
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
        ]
    }
    assert meta_1 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
        ),
        'urls': [
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
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
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }


def test_can_order_block_chunk_meta(api_client, file_blockchain_with_three_block_chunks):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=-start_block_number')

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['count'] == 3

    meta_0, meta_1, meta_2 = response_json['results']
    assert meta_2 == {
        'start_block_number':
            0,
        'end_block_number':
            2,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
        ),
        'urls': [
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.xz'
        ]
    }
    assert meta_1 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
        ),
        'urls': [
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
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
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }


def test_can_order_block_chunk_meta_with_limit(api_client, file_blockchain_with_three_block_chunks):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=-start_block_number&limit=2')

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['count'] == 3

    meta_0, meta_1 = response_json['results']
    assert meta_1 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
        ),
        'urls': [
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
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
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }


def test_can_order_block_chunk_meta_with_limit_and_offset(api_client, file_blockchain_with_three_block_chunks):

    blockchain = file_blockchain_with_three_block_chunks
    with force_blockchain(blockchain):
        response = api_client.get(API_V1_LIST_BLOCKCHAIN_STATE_URL + '?ordering=-start_block_number&limit=1&offset=1')

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['count'] == 3

    assert len(response_json['results']) == 1
    (meta_0,) = response_json['results']
    assert meta_0 == {
        'start_block_number':
            3,
        'end_block_number':
            5,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
        ),
        'urls': [
            'http://localhost:8555/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.xz'
        ]
    }
