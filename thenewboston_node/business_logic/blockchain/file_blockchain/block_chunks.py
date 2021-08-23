import os.path
import re
from collections import namedtuple

from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS

ORDER_OF_BLOCK = 20  # TODO(dmu) MEDIUM: Move to settings
BLOCK_CHUNK_FILENAME_TEMPLATE = '{start}-{end}-block-chunk.msgpack'


def make_block_chunk_filename(block_number, block_chunk_size):
    max_offset = block_chunk_size - 1
    chunk_number, offset = divmod(block_number, block_chunk_size)

    chunk_block_number_start = chunk_number * block_chunk_size
    chunk_block_number_end = chunk_block_number_start + max_offset

    start_block_str = str(chunk_block_number_start).zfill(ORDER_OF_BLOCK)
    end_block_str = 'x' * ORDER_OF_BLOCK

    if offset == max_offset:
        dest_end_block_str = str(chunk_block_number_end).zfill(ORDER_OF_BLOCK)
    else:
        assert offset < max_offset
        dest_end_block_str = end_block_str

    return (
        BLOCK_CHUNK_FILENAME_TEMPLATE.format(start=start_block_str, end=end_block_str),
        BLOCK_CHUNK_FILENAME_TEMPLATE.format(start=start_block_str, end=dest_end_block_str)
    )


BLOCK_CHUNK_FILENAME_RE = re.compile(
    BLOCK_CHUNK_FILENAME_TEMPLATE.format(start=r'(?P<start>\d+)', end=r'(?P<end>\d+|x+)') +
    r'(?:|\.(?P<compression>{}))$'.format('|'.join(COMPRESSION_FUNCTIONS.keys()))
)
BlockChunkFilenameMeta = namedtuple('BlockChunkFilenameMeta', 'start end compression')


def get_block_chunk_filename_meta(file_path):
    filename = os.path.basename(file_path)
    match = BLOCK_CHUNK_FILENAME_RE.match(filename)
    if match:
        start = int(match.group('start'))
        end_str = match.group('end')
        if ''.join(set(end_str)) == 'x':
            end = None
        else:
            end = int(end_str)
            assert start <= end

        return BlockChunkFilenameMeta(start, end, match.group('compression') or None)

    return None


def get_block_chunk_file_path_meta(file_path):
    return get_block_chunk_filename_meta(os.path.basename(file_path))
