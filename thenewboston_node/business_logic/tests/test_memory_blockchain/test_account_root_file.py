import copy

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain


def test_get_latest_account_root_file(forced_memory_blockchain: MemoryBlockchain, initial_account_root_file):
    account_root_files = forced_memory_blockchain.account_root_files
    assert len(account_root_files) == 1
    assert forced_memory_blockchain.get_closest_account_root_file() == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(-1) == initial_account_root_file

    account_root_file1 = copy.deepcopy(initial_account_root_file)
    account_root_file1.last_block_number = 3
    forced_memory_blockchain.account_root_files.append(account_root_file1)

    assert len(account_root_files) == 2
    assert forced_memory_blockchain.get_closest_account_root_file() == account_root_file1
    assert forced_memory_blockchain.get_closest_account_root_file(-1) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(0) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(1) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(2) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(3) == account_root_file1
    assert forced_memory_blockchain.get_closest_account_root_file(4) == account_root_file1

    account_root_file2 = copy.deepcopy(initial_account_root_file)
    account_root_file2.last_block_number = 5
    forced_memory_blockchain.account_root_files.append(account_root_file2)

    assert len(account_root_files) == 3
    assert forced_memory_blockchain.get_closest_account_root_file() == account_root_file2
    assert forced_memory_blockchain.get_closest_account_root_file(-1) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(0) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(1) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(2) == initial_account_root_file
    assert forced_memory_blockchain.get_closest_account_root_file(3) == account_root_file1
    assert forced_memory_blockchain.get_closest_account_root_file(4) == account_root_file1
    assert forced_memory_blockchain.get_closest_account_root_file(5) == account_root_file2
    assert forced_memory_blockchain.get_closest_account_root_file(6) == account_root_file2
