import copy

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain


def test_get_latest_account_root_file(memory_blockchain: MemoryBlockchain, blockchain_genesis_state):
    account_root_files = memory_blockchain.blockchain_states
    assert len(account_root_files) == 1
    assert memory_blockchain.get_last_blockchain_state() == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(-1) == blockchain_genesis_state

    account_root_file1 = copy.deepcopy(blockchain_genesis_state)
    account_root_file1.last_block_number = 3
    memory_blockchain.blockchain_states.append(account_root_file1)

    assert len(account_root_files) == 2
    assert memory_blockchain.get_last_blockchain_state() == account_root_file1
    assert memory_blockchain.get_blockchain_state_by_block_number(-1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(0) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(2) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(3) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(4) == account_root_file1

    account_root_file2 = copy.deepcopy(blockchain_genesis_state)
    account_root_file2.last_block_number = 5
    memory_blockchain.blockchain_states.append(account_root_file2)

    assert len(account_root_files) == 3
    assert memory_blockchain.get_last_blockchain_state() == account_root_file2
    assert memory_blockchain.get_blockchain_state_by_block_number(-1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(0) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(2) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(3) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(4) == account_root_file1
    assert memory_blockchain.get_blockchain_state_by_block_number(5) == account_root_file1
    assert memory_blockchain.get_blockchain_state_by_block_number(6) == account_root_file2
