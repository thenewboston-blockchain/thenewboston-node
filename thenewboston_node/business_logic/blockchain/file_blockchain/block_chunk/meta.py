import os.path
from collections import namedtuple
from typing import Optional

from thenewboston_node.business_logic.blockchain.file_blockchain.block_chunk.misc import BLOCK_CHUNK_FILENAME_RE
from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS

BlockChunkFilenameMeta = namedtuple(
    'BlockChunkFilenameMeta',
    'absolute_file_path blockchain_root_relative_file_path storage_relative_file_path filename base_filename '
    'start_block_number end_block_number compression blockchain'
)


# TODO(dmu) LOW: Make DRY with get_blockchain_state_filename_meta()
def get_block_chunk_filename_meta(
    *,
    absolute_file_path=None,
    blockchain_root_relative_file_path=None,
    storage_relative_file_path=None,
    filename=None,
    base_filename=None,
    blockchain=None,
) -> Optional[BlockChunkFilenameMeta]:
    assert absolute_file_path or blockchain_root_relative_file_path or storage_relative_file_path or filename

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

    match = BLOCK_CHUNK_FILENAME_RE.match(filename)
    if not match:
        return None

    start = int(match.group('start'))
    end_str = match.group('end')
    if ''.join(set(end_str)) == 'x':
        end = None
    else:
        end = int(end_str)
        assert start <= end

    return BlockChunkFilenameMeta(
        absolute_file_path=absolute_file_path,
        blockchain_root_relative_file_path=blockchain_root_relative_file_path,
        storage_relative_file_path=storage_relative_file_path,
        filename=filename,
        base_filename=base_filename,
        start_block_number=start,
        end_block_number=end,
        compression=match.group('compression') or None,
        blockchain=blockchain,
    )
