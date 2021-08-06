from contextlib import contextmanager

from thenewboston_node.business_logic.blockchain.base import BlockchainBase


@contextmanager
def force_blockchain(blockchain):
    try:
        BlockchainBase.set_instance_cache(blockchain)
        yield
    finally:
        BlockchainBase.clear_instance_cache()
