import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.types import hexstr


def test_validate_blockchain_state_raises(memory_blockchain: MemoryBlockchain):
    blockchain = memory_blockchain

    assert blockchain.blockchain_states
    for balance in blockchain.blockchain_states[0].account_states.values():
        balance.balance_lock = hexstr()
    with pytest.raises(ValidationError, match='Account state balance_lock must be not empty'):
        blockchain.validate_blockchain_states()

    blockchain.blockchain_states = []
    with pytest.raises(ValidationError, match='Blockchain must contain at least one blockchain state'):
        blockchain.validate_blockchain_states()
