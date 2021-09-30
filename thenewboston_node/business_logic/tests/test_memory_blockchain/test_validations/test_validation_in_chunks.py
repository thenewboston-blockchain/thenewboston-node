from tqdm import tqdm

from thenewboston_node.business_logic.tests.factories import make_large_blockchain
from thenewboston_node.core.utils.pytest import skip_slow


# This test is slow only if DEBUG level of logging is configured
# TODO(dmu) MEDIUM: Consider unmarking this test as slow
@skip_slow
def test_can_validate_blockchain_in_chunks(memory_blockchain, treasury_account_key_pair, primary_validator_key_pair):
    blockchain = memory_blockchain
    blockchain._test_primary_validator_key_pair = primary_validator_key_pair

    make_large_blockchain(blockchain, treasury_account_key_pair)
    blockchain.validate_blockchain_states()

    CHUNK_SIZE = 20
    block_count = blockchain.get_block_count()
    for offset in tqdm(range(0, block_count, CHUNK_SIZE)):
        blockchain.validate_blocks(offset=offset, limit=CHUNK_SIZE)


@skip_slow
def test_can_validate_blockchain_in_chunks_for_file_blockchain(file_blockchain, treasury_account_key_pair):
    blockchain = file_blockchain

    make_large_blockchain(blockchain, treasury_account_key_pair, blocks_count=99)
    blockchain.validate_blockchain_states()

    CHUNK_SIZE = 20
    block_count = blockchain.get_block_count()
    for offset in tqdm(range(0, block_count, CHUNK_SIZE)):
        blockchain.validate_blocks(offset=offset, limit=CHUNK_SIZE)
