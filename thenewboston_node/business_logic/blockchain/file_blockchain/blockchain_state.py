import os.path
import re
from collections import namedtuple

from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS

LAST_BLOCK_NUMBER_NONE_SENTINEL = '!'
BLOCKCHAIN_STATE_FILENAME_TEMPLATE = '{last_block_number}-blockchain-state.msgpack'
BLOCKCHAIN_STATE_FILENAME_RE = re.compile(
    BLOCKCHAIN_STATE_FILENAME_TEMPLATE.format(last_block_number=r'(?P<last_block_number>\d*(?:!|\d))') +
    r'(?:|\.(?P<compression>{}))$'.format('|'.join(COMPRESSION_FUNCTIONS.keys()))
)
BlockchainFilenameMeta = namedtuple('BlockchainFilenameMeta', 'last_block_number compression')


def make_blockchain_state_filename(last_block_number, block_number_digits_count):
    # We need to zfill LAST_BLOCK_NUMBER_NONE_SENTINEL to maintain the nested structure of directories
    prefix = (LAST_BLOCK_NUMBER_NONE_SENTINEL
              if last_block_number in (None, -1) else str(last_block_number)).zfill(block_number_digits_count)
    return BLOCKCHAIN_STATE_FILENAME_TEMPLATE.format(last_block_number=prefix)


def get_blockchain_state_filename_meta(filename):
    match = BLOCKCHAIN_STATE_FILENAME_RE.match(filename)
    if match:
        last_block_number_str = match.group('last_block_number')

        if last_block_number_str.endswith(LAST_BLOCK_NUMBER_NONE_SENTINEL):
            last_block_number = None
        else:
            last_block_number = int(last_block_number_str)

        return BlockchainFilenameMeta(last_block_number, match.group('compression') or None)

    return None


def get_blockchain_state_file_path_meta(file_path):
    return get_blockchain_state_filename_meta(os.path.basename(file_path))
