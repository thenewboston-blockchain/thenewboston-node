import copy

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.tests.factories import CoinTransferBlockFactory, CoinTransferBlockMessageFactory


def test_yield_blocks_till_snapshot(forced_memory_blockchain: MemoryBlockchain, blockchain_genesis_state):

    forced_memory_blockchain.blocks = [
        CoinTransferBlockFactory(message=CoinTransferBlockMessageFactory(block_number=x,
                                                                         block_identifier=str(x)))  # type: ignore
        for x in range(9)
    ]
    account_root_files = forced_memory_blockchain.blockchain_states
    assert len(account_root_files) == 1
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot() == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(-1) == blockchain_genesis_state
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot()
            ] == [8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(5)
            ] == [5, 4, 3, 2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(1)] == [1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(0)] == [0]

    account_root_file1 = copy.deepcopy(blockchain_genesis_state)
    account_root_file1.last_block_number = 3
    forced_memory_blockchain.blockchain_states.append(account_root_file1)

    assert len(account_root_files) == 2
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot() == account_root_file1
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(-1) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(0) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(1) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(2) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(3) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(4) == account_root_file1

    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot()
            ] == [8, 7, 6, 5, 4]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(5)] == [5, 4]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(3)] == []
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(2)
            ] == [2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(1)] == [1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(0)] == [0]

    account_root_file2 = copy.deepcopy(blockchain_genesis_state)
    account_root_file2.last_block_number = 5
    forced_memory_blockchain.blockchain_states.append(account_root_file2)

    assert len(account_root_files) == 3
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot() == account_root_file2
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(-1) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(0) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(1) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(2) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(3) == blockchain_genesis_state
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(4) == account_root_file1
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(5) == account_root_file1
    assert forced_memory_blockchain.get_closest_blockchain_state_snapshot(6) == account_root_file2

    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot()] == [8, 7, 6]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(8)
            ] == [8, 7, 6]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(7)] == [7, 6]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(6)] == [6]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(5)] == []
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(4)] == [4]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(3)] == []
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(2)
            ] == [2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(1)] == [1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.yield_blocks_till_snapshot(0)] == [0]
