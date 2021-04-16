import logging
import os.path
import re
from typing import Generator

import msgpack
from cachetools import LRUCache
from more_itertools import always_reversible, ilen

from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.storages.path_optimized_file_system import PathOptimizedFileSystemStorage
from thenewboston_node.core.logging import timeit

from .base import BlockchainBase

logger = logging.getLogger(__name__)

# TODO(dmu) LOW: Move these constants to configuration files
ORDER_OF_ACCOUNT_ROOT_FILE = 10
ORDER_OF_BLOCK = 20
BLOCK_CHUNK_SIZE = 100
BLOCK_CHUNK_FILENAME_TEMPLATE = '{start}-{end}-block-chunk.msgpack'
BLOCK_CHUNK_FILENAME_RE = re.compile(
    BLOCK_CHUNK_FILENAME_TEMPLATE.format(start=r'(?P<start>\d+)', end=r'(?P<end>\d+)')
)


def get_start_end(file_path):
    filename = os.path.basename(file_path)
    match = BLOCK_CHUNK_FILENAME_RE.match(filename)
    if match:
        return int(match.group('start')), int(match.group('end'))

    return None, None


class FileBlockchain(BlockchainBase):

    def __init__(self, base_directory, validate=True, account_root_files_cache_size=128, blocks_cache_size=1024):
        if not os.path.isabs(base_directory):
            raise ValueError('base_directory must be an absolute path')

        self.account_root_files_directory = os.path.join(base_directory, 'account-root-files')
        self.blocks_directory = os.path.join(base_directory, 'blocks')
        self.base_directory = base_directory

        self.storage = PathOptimizedFileSystemStorage()

        self.account_root_files_cache = LRUCache(account_root_files_cache_size)
        self.blocks_cache = LRUCache(blocks_cache_size)

        if validate:
            self.validate()

    # Account root files methods
    def persist_account_root_file(self, account_root_file: AccountRootFile):
        last_block_number = account_root_file.last_block_number

        prefix = ('.' if last_block_number is None else str(last_block_number)).zfill(ORDER_OF_ACCOUNT_ROOT_FILE)
        file_path = os.path.join(self.account_root_files_directory, f'{prefix}-arf.msgpack')
        self.storage.save(file_path, account_root_file.to_messagepack(), is_final=True)

    def _load_account_root_file(self, file_path):
        cache = self.account_root_files_cache
        account_root_file = cache.get(file_path)
        if account_root_file is None:
            storage = self.storage
            assert storage.is_finalized(file_path)
            account_root_file = AccountRootFile.from_messagepack(self.storage.load(file_path))
            cache[file_path] = account_root_file

        return account_root_file

    def _iter_account_root_files(self, direction) -> Generator[AccountRootFile, None, None]:
        assert direction in (1, -1)

        storage = self.storage
        for file_path in storage.list_directory(self.account_root_files_directory, sort_direction=direction):
            yield self._load_account_root_file(file_path)

    def iter_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        yield from self._iter_account_root_files(1)

    def iter_account_root_files_reversed(self) -> Generator[AccountRootFile, None, None]:
        yield from self._iter_account_root_files(-1)

    def get_account_root_file_count(self) -> int:
        return ilen(self.storage.list_directory(self.account_root_files_directory))

    # Blocks methods
    def persist_block(self, block: Block):
        block_number = block.message.block_number
        chunk_number, offset = divmod(block_number, BLOCK_CHUNK_SIZE)

        chunk_block_number_start = chunk_number * BLOCK_CHUNK_SIZE
        start_str = str(chunk_block_number_start).zfill(ORDER_OF_BLOCK)
        end_str = str(block_number).zfill(ORDER_OF_BLOCK)

        if chunk_block_number_start == block_number:
            append_end_str = str(block_number).zfill(ORDER_OF_BLOCK)
        else:
            assert chunk_block_number_start < block_number
            append_end_str = str(block_number - 1).zfill(ORDER_OF_BLOCK)

        append_filename = BLOCK_CHUNK_FILENAME_TEMPLATE.format(start=start_str, end=append_end_str)
        filename = BLOCK_CHUNK_FILENAME_TEMPLATE.format(start=start_str, end=end_str)

        append_file_path = os.path.join(self.blocks_directory, append_filename)
        self.storage.append(append_file_path, block.to_messagepack())

        file_path = os.path.join(self.blocks_directory, filename)
        if append_filename != filename:
            self.storage.move(append_file_path, file_path)

        if offset == BLOCK_CHUNK_SIZE - 1:
            self.storage.finalize(file_path)

    def iter_blocks(self) -> Generator[Block, None, None]:
        yield from self._iter_blocks(1)

    def iter_blocks_reversed(self) -> Generator[Block, None, None]:
        yield from self._iter_blocks(-1)

    def get_block_count(self) -> int:
        return ilen(self.storage.list_directory(self.blocks_directory))

    def _iter_blocks(self, direction) -> Generator[Block, None, None]:
        assert direction in (1, -1)

        storage = self.storage
        for file_path in storage.list_directory(self.blocks_directory, sort_direction=direction):
            start, end = get_start_end(file_path)
            assert start is not None
            assert end is not None
            last_block_number = None
            for block in self._iter_blocks_from_cache(start, end, direction):
                last_block_number = block.message.block_number
                yield block

            assert last_block_number is None or last_block_number <= end
            if last_block_number == end:
                continue

            yield from self._iter_blocks_from_file(file_path, direction, start=last_block_number)

    @timeit(verbose_args=True, is_method=True)
    def _iter_blocks_from_file(self, file_path, direction, start=None):
        assert direction in (1, -1)

        unpacker = msgpack.Unpacker()
        unpacker.feed(self.storage.load(file_path))
        if direction == -1:
            unpacker = always_reversible(unpacker)

        for block_compact_dict in unpacker:
            block = Block.from_compact_dict(block_compact_dict)
            block_number = block.message.block_number
            # TODO(dmu) HIGH: Implement a better skip
            if start is not None:
                if direction == 1 and block_number <= start:
                    continue
                elif direction == -1 and block_number >= start:
                    continue

            self.blocks_cache[block_number] = block
            yield block

    @timeit(verbose_args=True, is_method=True)
    def _iter_blocks_from_cache(self, start_block_number, end_block_number, direction):
        assert direction in (1, -1)

        iter_ = range(start_block_number, end_block_number + 1)
        if direction == -1:
            iter_ = always_reversible(iter_)

        for key in iter_:
            block = self.blocks_cache.get(key)
            if block is None:
                break

            yield block
