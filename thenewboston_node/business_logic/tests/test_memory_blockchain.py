import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain


@pytest.mark.usefixtures('use_memory_blockchain')
def test_can_use_memory_blockchain():
    assert isinstance(BlockchainBase.get_instance(), MemoryBlockchain)


@pytest.mark.usefixtures('use_memory_blockchain')
def test_get_initial_account_root_file(initial_account_root_file):
    assert BlockchainBase.get_instance().get_initial_account_root_file() == initial_account_root_file
