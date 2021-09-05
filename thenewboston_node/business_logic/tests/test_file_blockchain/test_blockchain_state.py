import os.path

import pytest

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain


@pytest.mark.parametrize('always_compress', (True, False))
def test_blockchain_state_file_exists(blockchain_directory, blockchain_genesis_state, always_compress):
    blockchain = FileBlockchain(
        base_directory=blockchain_directory, blockchain_state_storage_kwargs={'always_compress': always_compress}
    )
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain_states = list(blockchain.yield_blockchain_states())

    assert len(blockchain_states) == 1
    file_path = os.path.join(blockchain_directory, blockchain_states[0].meta['file_path'])
    assert os.path.exists(file_path)
