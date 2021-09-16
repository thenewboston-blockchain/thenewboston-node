import re

from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS

LAST_BLOCK_NUMBER_NONE_SENTINEL = '!'
BLOCKCHAIN_STATE_FILENAME_TEMPLATE = '{last_block_number}-blockchain-state.msgpack'
BLOCKCHAIN_STATE_FILENAME_RE = re.compile(
    BLOCKCHAIN_STATE_FILENAME_TEMPLATE.format(last_block_number=r'(?P<last_block_number>\d*(?:!|\d))') +
    r'(?:|\.(?P<compression>{}))$'.format('|'.join(COMPRESSION_FUNCTIONS.keys()))
)
