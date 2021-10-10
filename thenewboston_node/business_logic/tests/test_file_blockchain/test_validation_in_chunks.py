from tqdm import tqdm

from thenewboston_node.business_logic.tests.factories import make_large_blockchain
from thenewboston_node.core.utils.pytest import skip_slow


@skip_slow
def test_can_validate_file_blockchain_in_chunks(file_blockchain, treasury_account_key_pair):
    blockchain = file_blockchain

    make_large_blockchain(blockchain, treasury_account_key_pair, blocks_count=99)
    blockchain.validate_blockchain_states()

    CHUNK_SIZE = 20
    block_count = blockchain.get_block_count()
    for offset in tqdm(range(0, block_count, CHUNK_SIZE)):
        blockchain.validate_blocks(offset=offset, limit=CHUNK_SIZE)
