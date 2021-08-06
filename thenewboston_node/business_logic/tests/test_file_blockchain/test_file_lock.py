import os
from concurrent.futures import ThreadPoolExecutor

import filelock
import pytest

from thenewboston_node.business_logic.exceptions import BlockchainLockedError
from thenewboston_node.business_logic.tests import factories


def test_add_blockchain_state_is_thread_safe(file_blockchain, blockchain_directory, blockchain_genesis_state):
    lock_file_path = os.path.join(blockchain_directory, 'file.lock')
    pool = ThreadPoolExecutor()

    with filelock.FileLock(lock_file_path):
        future = pool.submit(file_blockchain.add_blockchain_state, blockchain_genesis_state)

        with pytest.raises(BlockchainLockedError, match='Blockchain locked*'):
            future.result(timeout=1)


def test_add_block_is_thread_safe(file_blockchain, blockchain_directory):
    lock_file_path = os.path.join(blockchain_directory, 'file.lock')
    pool = ThreadPoolExecutor()
    block_0 = factories.CoinTransferBlockFactory()

    with filelock.FileLock(lock_file_path):
        future = pool.submit(file_blockchain.add_block, block_0, validate=False)

        with pytest.raises(BlockchainLockedError, match='Blockchain locked*'):
            future.result(timeout=1)
