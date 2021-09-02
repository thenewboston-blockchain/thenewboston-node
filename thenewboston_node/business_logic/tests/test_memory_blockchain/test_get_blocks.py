import copy

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.tests.factories import CoinTransferBlockFactory, CoinTransferBlockMessageFactory


def test_yield_blocks_till_snapshot(memory_blockchain: MemoryBlockchain, blockchain_genesis_state):

    memory_blockchain.blocks = [
        CoinTransferBlockFactory(message=CoinTransferBlockMessageFactory(block_number=x,
                                                                         block_identifier=str(x)))  # type: ignore
        for x in range(9)
    ]
    account_root_files = memory_blockchain.blockchain_states
    assert len(account_root_files) == 1
    assert memory_blockchain.get_last_blockchain_state() == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(-1) == blockchain_genesis_state
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot()
            ] == [8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(5)
            ] == [5, 4, 3, 2, 1, 0]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(1)] == [1, 0]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(0)] == [0]

    blockchain_state_1 = copy.deepcopy(blockchain_genesis_state)
    blockchain_state_1.last_block_number = 3
    memory_blockchain.blockchain_states.append(blockchain_state_1)

    assert len(account_root_files) == 2
    assert memory_blockchain.get_last_blockchain_state() == blockchain_state_1
    assert memory_blockchain.get_blockchain_state_by_block_number(-1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(0) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(2) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(3) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(4) == blockchain_state_1

    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot()] == [8, 7, 6, 5, 4]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(5)] == [5, 4]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(3)] == []
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(2)] == [2, 1, 0]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(1)] == [1, 0]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(0)] == [0]

    blockchain_state_2 = copy.deepcopy(blockchain_genesis_state)
    blockchain_state_2.last_block_number = 5
    memory_blockchain.blockchain_states.append(blockchain_state_2)

    assert len(account_root_files) == 3
    assert memory_blockchain.get_last_blockchain_state() == blockchain_state_2
    assert memory_blockchain.get_blockchain_state_by_block_number(-1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(0) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(1) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(2) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(3) == blockchain_genesis_state
    assert memory_blockchain.get_blockchain_state_by_block_number(4) == blockchain_state_1
    assert memory_blockchain.get_blockchain_state_by_block_number(5) == blockchain_state_1
    assert memory_blockchain.get_blockchain_state_by_block_number(6) == blockchain_state_2

    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot()] == [8, 7, 6]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(8)] == [8, 7, 6]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(7)] == [7, 6]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(6)] == [6]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(5)] == []
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(4)] == [4]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(3)] == []
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(2)] == [2, 1, 0]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(1)] == [1, 0]
    assert [block.message.block_number for block in memory_blockchain.yield_blocks_till_snapshot(0)] == [0]
