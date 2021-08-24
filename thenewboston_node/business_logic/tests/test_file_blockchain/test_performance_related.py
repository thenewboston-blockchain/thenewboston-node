from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.tests.factories import CoinTransferBlockFactory


def test_yield_blocks_from_cache(blockchain_directory):
    blockchain = FileBlockchain(base_directory=blockchain_directory)
    block_cache = blockchain.get_block_cache()
    block_cache[0] = block0 = CoinTransferBlockFactory(hash='0')
    block_cache[1] = block1 = CoinTransferBlockFactory(hash='1')
    block_cache[2] = block2 = CoinTransferBlockFactory(hash='2')
    block_cache[3] = block3 = CoinTransferBlockFactory(hash='3')
    assert block0

    assert list(blockchain._yield_blocks_from_cache(1, 10, 1)) == [block1, block2, block3]
    assert list(blockchain._yield_blocks_from_cache(1, 2, 1)) == [block1, block2]
    assert list(blockchain._yield_blocks_from_cache(0, 3, -1)) == [block3, block2, block1, block0]
    assert list(blockchain._yield_blocks_from_cache(1, 2, -1)) == [block2, block1]
