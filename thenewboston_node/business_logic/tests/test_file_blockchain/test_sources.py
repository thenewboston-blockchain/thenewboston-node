from contextlib import closing
from io import BytesIO
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import pytest

from thenewboston_node.business_logic.blockchain.file_blockchain.sources import (
    BinaryDataBlockSource, BinaryDataStreamBlockSource, FileBlockSource, URLBlockSource
)
from thenewboston_node.business_logic.tests.baker_factories import make_coin_transfer_block


@pytest.mark.order(0)
def test_binary_data_block_source_iter():
    source = BinaryDataBlockSource(b'')
    blocks = tuple(iter(source))
    assert blocks == ()


@pytest.mark.order(0)
def test_can_get_blocks_from_binary_data_block_source():
    block1 = make_coin_transfer_block(meta=None)
    block2 = make_coin_transfer_block(meta=None)
    binary_data = b''.join((block1.to_messagepack(), block2.to_messagepack()))
    source = BinaryDataBlockSource(binary_data)

    blocks = tuple(source)

    assert blocks == (block1, block2)


@pytest.mark.order(1)
def test_can_get_blocks_from_binary_data_block_source_in_reverse_direction():
    block1 = make_coin_transfer_block(meta=None)
    block2 = make_coin_transfer_block(meta=None)
    binary_data = b''.join((block1.to_messagepack(), block2.to_messagepack()))
    source = BinaryDataBlockSource(binary_data, direction=-1)

    blocks = tuple(source)

    assert blocks == (block2, block1)


@pytest.mark.order(0)
def test_can_get_blocks_from_binary_data_stream_block_source():
    block1 = make_coin_transfer_block(meta=None)
    block2 = make_coin_transfer_block(meta=None)
    binary_data = b''.join((block1.to_messagepack(), block2.to_messagepack()))

    source = BinaryDataStreamBlockSource(BytesIO(binary_data))
    blocks = tuple(source)
    assert blocks == (block1, block2)

    source = BinaryDataStreamBlockSource(BytesIO(binary_data), direction=-1)
    blocks = tuple(source)
    assert blocks == (block2, block1)


@pytest.mark.order(0)
def test_can_get_blocks_from_file_block_source():
    block1 = make_coin_transfer_block(meta=None)
    block2 = make_coin_transfer_block(meta=None)
    binary_data = b''.join((block1.to_messagepack(), block2.to_messagepack()))

    with NamedTemporaryFile() as fo:
        fo.write(binary_data)
        fo.flush()
        with closing(FileBlockSource(fo.name)) as source:
            blocks = tuple(source)
            assert blocks == (block1, block2)

    with NamedTemporaryFile() as fo:
        fo.write(binary_data)
        fo.flush()
        with closing(FileBlockSource(fo.name, direction=-1)) as source:
            blocks = tuple(source)
            assert blocks == (block2, block1)


@pytest.mark.order(0)
def test_can_get_blocks_from_url_block_source(outer_web_mock):
    block1 = make_coin_transfer_block(meta=None)
    block2 = make_coin_transfer_block(meta=None)
    binary_data = b''.join((block1.to_messagepack(), block2.to_messagepack()))

    url = (
        'http://example.com/blockchain/blockchain-chunks'
        '/0/0/0/0/0/0/0/0/000000000012-000000000101-block-chunk.msgpack'
    )
    outer_web_mock.register_uri(
        outer_web_mock.GET, url, body=binary_data, adding_headers={'Content-Type': 'application/octet-stream'}
    )
    with urlopen(url) as fo:
        assert fo.read() == binary_data

    with closing(URLBlockSource(url)) as source:
        blocks = tuple(source)
        assert blocks == (block1, block2)

    with closing(URLBlockSource(url, direction=-1)) as source:
        blocks = tuple(source)
        assert blocks == (block2, block1)
