from contextlib import closing
from io import BytesIO
from tempfile import NamedTemporaryFile

import pytest

from thenewboston_node.business_logic.blockchain.file_blockchain.sources import (
    BinaryDataBlockSource, BinaryDataStreamBlockSource, FileBlockSource
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
