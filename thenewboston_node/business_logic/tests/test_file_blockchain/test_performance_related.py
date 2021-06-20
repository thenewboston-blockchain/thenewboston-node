from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain, get_start_end
from thenewboston_node.business_logic.tests.factories import CoinTransferBlockFactory


def test_yield_blocks_from_cache(blockchain_directory):
    blockchain = FileBlockchain(base_directory=blockchain_directory)
    blockchain.blocks_cache[0] = block0 = CoinTransferBlockFactory(hash='0')
    blockchain.blocks_cache[1] = block1 = CoinTransferBlockFactory(hash='1')
    blockchain.blocks_cache[2] = block2 = CoinTransferBlockFactory(hash='2')
    blockchain.blocks_cache[3] = block3 = CoinTransferBlockFactory(hash='3')
    assert block0

    assert list(blockchain._yield_blocks_from_cache(1, 10, 1)) == [block1, block2, block3]
    assert list(blockchain._yield_blocks_from_cache(1, 2, 1)) == [block1, block2]
    assert list(blockchain._yield_blocks_from_cache(0, 3, -1)) == [block3, block2, block1, block0]
    assert list(blockchain._yield_blocks_from_cache(1, 2, -1)) == [block2, block1]


def test_get_start_end():
    assert get_start_end('00012-000101-block-chunk.msgpack') == (12, 101)
