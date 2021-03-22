import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain


@pytest.mark.usefixtures('forced_memory_blockchain')
def test_can_force_memory_blockchain():
    assert isinstance(BlockchainBase.get_instance(), MemoryBlockchain)
