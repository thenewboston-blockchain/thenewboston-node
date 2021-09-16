from collections import namedtuple

from thenewboston_node.business_logic.blockchain.file_blockchain.blockchain_state.misc import (
    BLOCKCHAIN_STATE_FILENAME_RE, LAST_BLOCK_NUMBER_NONE_SENTINEL
)

BlockchainFilenameMeta = namedtuple('BlockchainFilenameMeta', 'last_block_number compression')


def get_blockchain_state_filename_meta(filename):
    match = BLOCKCHAIN_STATE_FILENAME_RE.match(filename)
    if not match:
        return None

    last_block_number_str = match.group('last_block_number')

    if last_block_number_str.endswith(LAST_BLOCK_NUMBER_NONE_SENTINEL):
        last_block_number = None
    else:
        last_block_number = int(last_block_number_str)

    return BlockchainFilenameMeta(last_block_number, match.group('compression') or None)
