import pytest
from tqdm import tqdm

from thenewboston_node.core.utils.pytest import skip_slow


# This test is slow only if DEBUG level of logging is configured
# TODO(dmu) MEDIUM: Consider unmarking this test as slow
@skip_slow
@pytest.mark.usefixtures('forced_memory_blockchain')
def test_can_validate_blockchain_in_chunks(large_blockchain):
    blockchain = large_blockchain
    blockchain.validate_account_root_files()

    CHUNK_SIZE = 20
    block_count = large_blockchain.get_block_count()
    for offset in tqdm(range(0, block_count, CHUNK_SIZE)):
        large_blockchain.validate_blocks(offset=offset, limit=CHUNK_SIZE)


@skip_slow
@pytest.mark.usefixtures('forced_file_blockchain')
def test_can_validate_blockchain_in_chunks_for_file_blockchain(large_blockchain):
    blockchain = large_blockchain
    blockchain.validate_account_root_files()

    CHUNK_SIZE = 20
    block_count = large_blockchain.get_block_count()
    for offset in tqdm(range(0, block_count, CHUNK_SIZE)):
        large_blockchain.validate_blocks(offset=offset, limit=CHUNK_SIZE)
