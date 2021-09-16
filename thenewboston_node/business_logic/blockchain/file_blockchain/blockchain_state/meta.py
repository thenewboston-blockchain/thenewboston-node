import os.path
from collections import namedtuple

from thenewboston_node.business_logic.blockchain.file_blockchain.blockchain_state.misc import (
    BLOCKCHAIN_STATE_FILENAME_RE, LAST_BLOCK_NUMBER_NONE_SENTINEL
)
from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS

BlockchainFilenameMeta = namedtuple(
    'BlockchainFilenameMeta',
    'absolute_file_path blockchain_root_relative_file_path storage_relative_file_path filename base_filename '
    'last_block_number compression blockchain'
)


# TODO(dmu) LOW: Make DRY with get_block_chunk_filename_meta()
def get_blockchain_state_filename_meta(
    *,
    absolute_file_path=None,
    blockchain_root_relative_file_path=None,
    storage_relative_file_path=None,
    filename=None,
    base_filename=None,
    blockchain=None,
):
    assert (absolute_file_path or blockchain_root_relative_file_path or storage_relative_file_path or filename)

    filename = filename or os.path.basename(
        absolute_file_path or blockchain_root_relative_file_path or storage_relative_file_path
    )
    if base_filename is None:
        base_filename = filename
        for compressor in COMPRESSION_FUNCTIONS.keys():
            ext = '.' + compressor
            if base_filename.endswith(ext):
                base_filename = base_filename.removesuffix(ext)
                break

    match = BLOCKCHAIN_STATE_FILENAME_RE.match(filename)
    if not match:
        return None

    last_block_number_str = match.group('last_block_number')
    if last_block_number_str.endswith(LAST_BLOCK_NUMBER_NONE_SENTINEL):
        last_block_number = None
    else:
        last_block_number = int(last_block_number_str)

    return BlockchainFilenameMeta(
        absolute_file_path=absolute_file_path,
        blockchain_root_relative_file_path=blockchain_root_relative_file_path,
        storage_relative_file_path=storage_relative_file_path,
        filename=filename,
        base_filename=base_filename,
        last_block_number=last_block_number,
        compression=match.group('compression') or None,
        blockchain=blockchain,
    )
