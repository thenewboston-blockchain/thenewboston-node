from urllib.parse import urljoin

import pytest

from thenewboston_node.business_logic.tests.base import force_blockchain, force_file_blockchain


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
    with force_blockchain(file_blockchain):
        result = node_client.list_block_chunks_meta_by_network_address('http://testserver/')

    assert result == []


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_list_block_chunks_meta_by_network_address(
    node_client, file_blockchain_with_five_block_chunks, pv_network_address
):
    with force_blockchain(file_blockchain_with_five_block_chunks):
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
    with force_blockchain(file_blockchain_with_five_block_chunks):
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
    with force_blockchain(file_blockchain_with_five_block_chunks):
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
    with force_blockchain(file_blockchain_with_five_block_chunks):
        result = node_client.list_block_chunks_meta_by_network_address(
            'http://testserver/', from_block_number=7, direction=direction
        )
    assert [(item['start_block_number'], item['end_block_number']) for item in result] == [(6, 8), (9, 11),
                                                                                           (12, 13)][::direction]

    with force_blockchain(file_blockchain_with_five_block_chunks):
        result = node_client.list_block_chunks_meta_by_network_address(
            'http://testserver/', to_block_number=7, direction=direction
        )
    assert [(item['start_block_number'], item['end_block_number']) for item in result] == [(0, 2), (3, 5),
                                                                                           (6, 8)][::direction]

    with force_blockchain(file_blockchain_with_five_block_chunks):
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

    with force_file_blockchain(blockchain, outer_web_mock, pv_network_address):
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
