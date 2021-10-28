from urllib.parse import urljoin

import pytest

from thenewboston_node.business_logic.tests.base import as_primary_validator, force_blockchain, force_file_blockchain


def test_get_latest_blockchain_state_meta_by_network_address(
    node_client, node_mock, blockchain_state_meta, another_node_network_address
):
    # TODO(dmu) MEDIUM: Refactor to use `node_mock_for_node_client` fixture
    result = node_client.get_latest_blockchain_state_meta_by_network_address(another_node_network_address)
    assert result == blockchain_state_meta
    assert node_mock.latest_requests()[-1].url.startswith(
        urljoin(another_node_network_address, 'api/v1/blockchain-states-meta/')
    )


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_empty_list_block_chunks_meta_by_network_address(node_client, file_blockchain):
    with force_blockchain(file_blockchain), as_primary_validator():
        result = node_client.list_block_chunks_meta_by_network_address('http://testserver/')

    assert result == []


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_list_block_chunks_meta_by_network_address(
    node_client, file_blockchain_with_five_block_chunks, pv_network_address
):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        result = node_client.list_block_chunks_meta_by_network_address('http://testserver/')

    assert result == [{
        'end_block_number':
            2,
        'start_block_number':
            0,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ]
    }, {
        'end_block_number':
            5,
        'start_block_number':
            3,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000003-00000000000000000005-block-chunk.msgpack.gz'
        ]
    }, {
        'end_block_number':
            8,
        'start_block_number':
            6,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-00000000000000000008-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000006-00000000000000000008-block-chunk.msgpack.gz'
        ]
    }, {
        'end_block_number':
            11,
        'start_block_number':
            9,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000009-00000000000000000011-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000009-00000000000000000011-block-chunk.msgpack.gz'
        ]
    }, {
        'end_block_number':
            13,
        'start_block_number':
            12,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000012-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000012-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }]


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_limit_list_block_chunks_meta_by_network_address(
    node_client, file_blockchain_with_five_block_chunks, pv_network_address
):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        result = node_client.list_block_chunks_meta_by_network_address('http://testserver/', limit=1)

    assert result == [{
        'end_block_number':
            2,
        'start_block_number':
            0,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000000-00000000000000000002-block-chunk.msgpack.gz'
        ]
    }]


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_reversed_list_block_chunks_meta_by_network_address(
    node_client, file_blockchain_with_five_block_chunks, pv_network_address
):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        result = node_client.list_block_chunks_meta_by_network_address('http://testserver/', limit=2, direction=-1)

    assert result == [{
        'end_block_number':
            13,
        'start_block_number':
            12,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000012-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000012-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
        ]
    }, {
        'end_block_number':
            11,
        'start_block_number':
            9,
        'url_path': (
            '/blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000009-00000000000000000011-block-chunk.msgpack.gz'
        ),
        'urls': [
            f'{pv_network_address}blockchain/block-chunks/0/0/0/0/0/0/0/0/'
            '00000000000000000009-00000000000000000011-block-chunk.msgpack.gz'
        ]
    }]


@pytest.mark.parametrize('direction', (1, -1))
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_from_to_block_number_list_block_chunks_meta_by_network_address(
    node_client, file_blockchain_with_five_block_chunks, direction
):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        result = node_client.list_block_chunks_meta_by_network_address(
            'http://testserver/', from_block_number=7, direction=direction
        )
    assert [(item['start_block_number'], item['end_block_number']) for item in result] == [(6, 8), (9, 11),
                                                                                           (12, 13)][::direction]

    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        result = node_client.list_block_chunks_meta_by_network_address(
            'http://testserver/', to_block_number=7, direction=direction
        )
    assert [(item['start_block_number'], item['end_block_number']) for item in result] == [(0, 2), (3, 5),
                                                                                           (6, 8)][::direction]

    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        result = node_client.list_block_chunks_meta_by_network_address(
            'http://testserver/', from_block_number=4, to_block_number=9, direction=direction
        )
    assert [(item['start_block_number'], item['end_block_number']) for item in result] == [(3, 5), (6, 8),
                                                                                           (9, 11)][::direction]


@pytest.mark.parametrize(
    'from_block_number,to_block_number',
    (
        (12, 13),
        (0, 0),  # one block
        (0, 2),  # all blocks in the save chunk
        (3, 5),  # all blocks in the save chunk 2
        (3, 7),
        (12, None),
        (8, 13),
        (8, None),
        (None, 5),
        (None, None),
        (0, 13),
        (10, 15),
    )
)
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_yield_blocks_slice(
    node_client, file_blockchain_with_five_block_chunks, outer_web_mock, from_block_number, to_block_number,
    pv_network_address
):
    blockchain = file_blockchain_with_five_block_chunks
    last_block_number = blockchain.get_last_block_number()
    assert last_block_number == 13

    with force_file_blockchain(blockchain, outer_web_mock, pv_network_address), as_primary_validator():
        blocks = list(
            node_client.yield_blocks_slice(
                'http://testserver/', from_block_number=from_block_number, to_block_number=to_block_number
            )
        )

    from_block_number_expected = from_block_number or 0
    to_block_number_expected = min(
        last_block_number if to_block_number is None else to_block_number, last_block_number
    )
    assert [block.get_block_number() for block in blocks
            ] == list(range(from_block_number_expected, to_block_number_expected + 1, 1))


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_list_nodes(node_client, file_blockchain_with_five_block_chunks, pv_network_address):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        result = node_client.list_nodes('http://testserver/')
        assert result == {
            'count':
                3,
            'results': [{
                'fee_account': None,
                'fee_amount': 4,
                'identifier': 'b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1',
                'network_addresses': ['http://pv.non-existing-domain:8555/'],
                'role': 1
            }, {
                'fee_account': None,
                'fee_amount': 1,
                'identifier': '0c838f7f50020ea586b2cd26b4f3cc7b5b399161af43e584f0cc3110952e3c05',
                'network_addresses': ['http://cv.non-existing-domain:8555/'],
                'role': 2
            }, {
                'fee_account': None,
                'fee_amount': 1,
                'identifier': '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',
                'network_addresses': ['http://preferred-node.non-existing-domain:8555/'],
                'role': 3
            }]
        }


@pytest.mark.parametrize(
    'identifier,is_online_expected',
    (
        ('b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1', True),
        ('WRONG_IDENTIFIER', False),  # one block
    )
)
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_is_node_online(
    node_client, file_blockchain_with_five_block_chunks, pv_network_address, identifier, is_online_expected
):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        is_online = node_client.is_node_online('http://testserver/', identifier)
        assert is_online is is_online_expected
