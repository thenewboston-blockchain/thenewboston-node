from django.test import override_settings

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain.base import FileBlockchain
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain

MEMORY_BLOCKCHAIN_CLASS = 'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain'
FILE_BLOCKCHAIN_CLASS = 'thenewboston_node.business_logic.blockchain.file_blockchain.FileBlockchain'


def test_get_instance(blockchain_directory):
    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN={'class': MEMORY_BLOCKCHAIN_CLASS, 'kwargs': {}}):
        blockchain = BlockchainBase.get_instance()
        assert isinstance(blockchain, MemoryBlockchain)
    BlockchainBase.clear_instance_cache()

    with override_settings(
        BLOCKCHAIN={
            'class': FILE_BLOCKCHAIN_CLASS,
            'kwargs': {
                'base_directory': blockchain_directory
            }
        }
    ):
        blockchain = BlockchainBase.get_instance()
        assert isinstance(blockchain, FileBlockchain)
    BlockchainBase.clear_instance_cache()
