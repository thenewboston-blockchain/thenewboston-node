import logging
import os.path
import re
from collections import namedtuple
from typing import Any, Callable, Generator, Optional, Union, cast

import filelock
import msgpack
from cachetools import LRUCache
from more_itertools import always_reversible, ilen

from thenewboston_node.business_logic.exceptions import BlockchainLockedError, BlockchainUnlockedError
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS
from thenewboston_node.business_logic.storages.path_optimized_file_system import PathOptimizedFileSystemStorage
from thenewboston_node.core.logging import timeit
from thenewboston_node.core.utils.file_lock import ensure_locked, lock_method

from ..base import BlockchainBase

logger = logging.getLogger(__name__)

# TODO(dmu) LOW: Move these constants to configuration files
ORDER_OF_BLOCKCHAIN_STATE_FILE = 10
ORDER_OF_BLOCK = 20

LAST_BLOCK_NUMBER_NONE_SENTINEL = '!'
# We need to zfill to maintain the nested structure of directories
BLOCKCHAIN_GENESIS_STATE_PREFIX = LAST_BLOCK_NUMBER_NONE_SENTINEL.zfill(ORDER_OF_BLOCKCHAIN_STATE_FILE)

BLOCKCHAIN_STATE_FILENAME_TEMPLATE = '{last_block_number}-blockchain-state.msgpack'
BLOCKCHAIN_STATE_FILENAME_RE = re.compile(
    BLOCKCHAIN_STATE_FILENAME_TEMPLATE.
    format(last_block_number=r'(?P<last_block_number>\d{,' + str(ORDER_OF_BLOCKCHAIN_STATE_FILE - 1) + r'}(?:!|\d))') +
    r'(?:|\.(?P<compression>{}))$'.format('|'.join(COMPRESSION_FUNCTIONS.keys()))
)

BLOCK_CHUNK_FILENAME_TEMPLATE = '{start}-{end}-block-chunk.msgpack'
BLOCK_CHUNK_FILENAME_RE = re.compile(
    BLOCK_CHUNK_FILENAME_TEMPLATE.format(start=r'(?P<start>\d+)', end=r'(?P<end>\d+|x+)') +
    r'(?:|\.(?P<compression>{}))$'.format('|'.join(COMPRESSION_FUNCTIONS.keys()))
)
INCOMPLETE_BLOCK_CHUNK_END_BLOCK_NUMBER_SENTINEL = 'x' * ORDER_OF_BLOCK

DEFAULT_BLOCKCHAIN_STATES_SUBDIR = 'blockchain-states'
DEFAULT_BLOCKS_SUBDIR = 'blocks'

DEFAULT_BLOCK_CHUNK_SIZE = 100

LOCKED_EXCEPTION = BlockchainLockedError('Blockchain locked. Probably it is being modified by another process')
EXPECTED_LOCK_EXCEPTION = BlockchainUnlockedError('Blockchain was expected to be locked')

BlockChunkFilenameMeta = namedtuple('BlockChunkFilenameMeta', 'start end compression')
BlockchainFilenameMeta = namedtuple('BlockchainFilenameMeta', 'last_block_number compression')


def make_blockchain_state_filename(last_block_number=None):
    # We need to zfill LAST_BLOCK_NUMBER_NONE_SENTINEL to maintain the nested structure of directories
    prefix = (LAST_BLOCK_NUMBER_NONE_SENTINEL
              if last_block_number is None else str(last_block_number)).zfill(ORDER_OF_BLOCKCHAIN_STATE_FILE)
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


class FileBlockchain(BlockchainBase):

    def __init__(
        self,
        *,
        base_directory,

        # Account root files
        account_root_files_subdir=DEFAULT_BLOCKCHAIN_STATES_SUBDIR,
        account_root_files_cache_size=128,
        account_root_files_storage_kwargs=None,

        # Blocks
        blocks_subdir=DEFAULT_BLOCKS_SUBDIR,
        block_chunk_size=DEFAULT_BLOCK_CHUNK_SIZE,
        blocks_cache_size=None,
        blocks_storage_kwargs=None,
        lock_filename='file.lock',
        **kwargs
    ):
        if not os.path.isabs(base_directory):
            raise ValueError('base_directory must be an absolute path')

        kwargs.setdefault('snapshot_period_in_blocks', block_chunk_size)
        super().__init__(**kwargs)

        self.block_chunk_size = block_chunk_size

        self.blockchain_states_directory = os.path.join(base_directory, account_root_files_subdir)
        block_directory = os.path.join(base_directory, blocks_subdir)
        self.base_directory = base_directory

        self.block_storage = PathOptimizedFileSystemStorage(base_path=block_directory, **(blocks_storage_kwargs or {}))
        self.blockchain_states_storage = PathOptimizedFileSystemStorage(
            base_path=self.blockchain_states_directory, **(account_root_files_storage_kwargs or {})
        )

        self.account_root_files_cache_size = account_root_files_cache_size
        self.blocks_cache_size = blocks_cache_size

        self.blockchain_states_cache: Optional[LRUCache] = None
        self.blocks_cache: Optional[LRUCache] = None
        self.block_chunk_last_block_number_cache: Optional[LRUCache] = None
        self.initialize_caches()

        self._file_lock = None
        self.lock_filename = lock_filename

    @property
    def file_lock(self):
        file_lock = self._file_lock
        if file_lock is None:
            base_directory = self.base_directory
            os.makedirs(base_directory, exist_ok=True)
            lock_file_path = os.path.join(base_directory, self.lock_filename)
            self._file_lock = file_lock = filelock.FileLock(lock_file_path, timeout=0)

        return file_lock

    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def clear(self):
        self.initialize_caches()
        self.block_storage.clear()
        self.blockchain_states_storage.clear()

    def initialize_caches(self):
        self.blockchain_states_cache = LRUCache(self.account_root_files_cache_size)
        self.blocks_cache = LRUCache(
            # We do not really need to cache more than `snapshot_period_in_blocks` blocks since
            # we use use account root file as a base
            self.snapshot_period_in_blocks * 2 if self.blocks_cache_size is None else self.blocks_cache_size
        )
        self.block_chunk_last_block_number_cache = LRUCache(2)

    # Account root files methods
    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def add_blockchain_state(self, blockchain_state: BlockchainState):
        return super().add_blockchain_state(blockchain_state)

    @ensure_locked(lock_attr='file_lock', exception=EXPECTED_LOCK_EXCEPTION)
    def persist_blockchain_state(self, blockchain_state: BlockchainState):
        storage = self.blockchain_states_storage
        last_block_number = blockchain_state.last_block_number

        filename = make_blockchain_state_filename(last_block_number)
        storage.save(filename, blockchain_state.to_messagepack(), is_final=True)

    def _load_blockchain_state(self, file_path):
        logger.debug('Loading blockchain from %s', file_path)
        cache = self.blockchain_states_cache
        blockchain_state = cache.get(file_path)
        if blockchain_state is None:
            storage = self.blockchain_states_storage
            assert storage.is_finalized(file_path)
            blockchain_state = BlockchainState.from_messagepack(storage.load(file_path))

            meta = get_blockchain_state_filename_meta(file_path)
            blockchain_state.meta = {
                'file_path': self._get_blockchain_state_real_file_path(file_path),
                'last_block_number': meta.last_block_number,
                'compression': meta.compression,
                'blockchain': self,
            }
            cache[file_path] = blockchain_state
        else:
            logger.debug('Cache hit for %s', file_path)

        return blockchain_state

    def _yield_blockchain_states(
        self,
        direction,
        lazy=False
    ) -> Generator[Union[BlockchainState, Callable[[Any], BlockchainState]], None, None]:
        assert direction in (1, -1)

        for file_path in self.blockchain_states_storage.list_directory(sort_direction=direction):
            if lazy:
                yield cast(
                    Callable[[Any], BlockchainState],
                    lambda file_path_=file_path: self._load_blockchain_state(file_path_)
                )
            else:
                yield self._load_blockchain_state(file_path)

    def yield_blockchain_states(self,
                                lazy=False
                                ) -> Generator[Union[BlockchainState, Callable[[Any], BlockchainState]], None, None]:
        yield from self._yield_blockchain_states(1, lazy=lazy)

    def yield_blockchain_states_reversed(
        self, lazy=False
    ) -> Generator[Union[BlockchainState, Callable[[Any], BlockchainState]], None, None]:
        yield from self._yield_blockchain_states(-1, lazy=lazy)

    def get_blockchain_states_count(self) -> int:
        return ilen(self.blockchain_states_storage.list_directory())

    def _get_blockchain_state_real_file_path(self, file_path):
        optimized_path = self.blockchain_states_storage.get_optimized_path(file_path)
        abs_optimized_path = os.path.join(self.blockchain_states_directory, optimized_path)
        return os.path.relpath(abs_optimized_path, self.base_directory)

    # Blocks methods
    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def add_block(self, block: Block, validate=True):
        block_number = block.get_block_number()

        logger.debug('Adding block number %s to the blockchain', block_number)
        rv = super().add_block(block, validate)

        cache = self.block_chunk_last_block_number_cache
        assert cache is not None

        key = self._make_last_block_chunk_file_path_key()
        cache[key] = block_number

        return rv

    @ensure_locked(lock_attr='file_lock', exception=EXPECTED_LOCK_EXCEPTION)
    def persist_block(self, block: Block):
        append_filename, destination_filename = make_block_chunk_filename(
            block.get_block_number(), self.block_chunk_size
        )

        storage = self.block_storage
        storage.append(append_filename, block.to_messagepack())

        if append_filename == destination_filename:
            return

        storage.move(append_filename, destination_filename)
        storage.finalize(destination_filename)

        chunk_file_path = storage.get_optimized_actual_path(destination_filename)
        meta = get_block_chunk_file_path_meta(destination_filename)
        end = meta.end
        assert end is not None
        for block_number in range(meta.start, end + 1):
            block = self.blocks_cache.get(block_number)  # type: ignore
            if block is None:
                continue

            assert block.meta['chunk_file_path'].endswith(append_filename)  # type: ignore
            self._set_block_meta(block, meta, chunk_file_path)

    def get_current_chunk_filename(self):
        pass

    def yield_blocks(self) -> Generator[Block, None, None]:
        yield from self._yield_blocks(1)

    @timeit(verbose_args=True, is_method=True)
    def yield_blocks_reversed(self) -> Generator[Block, None, None]:
        yield from self._yield_blocks(-1)

    def yield_blocks_from(self, block_number: int) -> Generator[Block, None, None]:
        for file_path in self._list_block_directory():
            meta = self._get_block_chunk_file_path_meta_enhanced(file_path)
            if meta is None:
                logger.warning('File %s has invalid name format', file_path)
                continue

            if meta.end < block_number:
                continue

            yield from self._yield_blocks_from_file_cached(file_path, direction=1, start=max(meta.start, block_number))

    def get_block_by_number(self, block_number: int) -> Optional[Block]:
        assert self.blocks_cache is not None
        block = self.blocks_cache.get(block_number)
        if block is not None:
            return block

        try:
            return next(self.yield_blocks_from(block_number))
        except StopIteration:
            return None

    def get_block_count(self) -> int:
        count = 0
        for file_path in self._list_block_directory():
            meta = self._get_block_chunk_file_path_meta_enhanced(file_path)
            if meta is None:
                logger.warning('File %s has invalid name format', file_path)
                continue

            count += meta.end - meta.start + 1

        return count

    def get_next_block_number(self) -> int:
        last_block_chunk_file_path = self._get_last_block_chunk_file_path()
        if last_block_chunk_file_path is None:
            blockchain_state = self.get_last_blockchain_state()
            assert blockchain_state
            return blockchain_state.get_next_block_number()

        return self._get_block_chunk_last_block_number(last_block_chunk_file_path) + 1

    @timeit(verbose_args=True, is_method=True)
    def _yield_blocks(self, direction) -> Generator[Block, None, None]:
        assert direction in (1, -1)

        for file_path in self._list_block_directory(direction):
            yield from self._yield_blocks_from_file_cached(file_path, direction)

    def _yield_blocks_from_file_cached(self, file_path, direction, start=None):
        assert direction in (1, -1)

        meta = self._get_block_chunk_file_path_meta_enhanced(file_path)
        if meta is None:
            logger.warning('File %s has invalid name fyield_blocks_fromormat', file_path)
            return

        file_start = meta.start
        file_end = meta.end
        if direction == 1:
            next_block_number = cache_start = file_start if start is None else start
            cache_end = file_end
        else:
            cache_start = file_start
            next_block_number = cache_end = file_end if start is None else start

        for block in self._yield_blocks_from_cache(cache_start, cache_end, direction):
            assert next_block_number == block.message.block_number
            next_block_number += direction
            yield block

        if file_start <= next_block_number <= file_end:
            yield from self._yield_blocks_from_file(file_path, direction, start=next_block_number)

    @staticmethod
    def _set_block_meta(block, meta, chunk_file_path):
        block.meta = {
            'chunk_start_block': meta.start,
            'chunk_end_block': meta.end,
            'chunk_compression': meta.compression,
            'chunk_file_path': chunk_file_path
        }

    def _yield_blocks_from_file(self, file_path, direction, start=None):
        assert direction in (1, -1)
        storage = self.block_storage
        chunk_file_path = storage.get_optimized_actual_path(file_path)
        meta = get_block_chunk_file_path_meta(file_path)

        unpacker = msgpack.Unpacker()
        unpacker.feed(storage.load(file_path))
        if direction == -1:
            unpacker = always_reversible(unpacker)

        for block_compact_dict in unpacker:
            block = Block.from_compact_dict(block_compact_dict)
            block_number = block.message.block_number
            # TODO(dmu) HIGH: Implement a better skip
            if start is not None:
                if direction == 1 and block_number < start:
                    continue
                elif direction == -1 and block_number > start:
                    continue

            assert block.meta is None
            self._set_block_meta(block, meta, chunk_file_path)

            self.blocks_cache[block_number] = block
            yield block

    def _yield_blocks_from_cache(self, start_block_number, end_block_number, direction):
        assert direction in (1, -1)

        iter_ = range(start_block_number, end_block_number + 1)
        if direction == -1:
            iter_ = always_reversible(iter_)

        for block_number in iter_:
            block = self.blocks_cache.get(block_number)
            if block is None:
                break

            yield block

    def _list_block_directory(self, direction=1):
        yield from self.block_storage.list_directory(sort_direction=direction)

    def _get_last_block_chunk_file_path(self):
        try:
            return next(self._list_block_directory(-1))
        except StopIteration:
            return None

    def _make_last_block_chunk_file_path_key(self):
        return self._make_block_chunk_last_block_number_cache_key(self._get_last_block_chunk_file_path())

    def _make_block_chunk_last_block_number_cache_key(self, file_path):
        return file_path, self.block_storage.get_mtime(file_path)

    def _get_block_chunk_last_block_number(self, file_path):
        key = self._make_block_chunk_last_block_number_cache_key(file_path)
        block_chunk_last_block_number_cache = self.block_chunk_last_block_number_cache
        last_block_number = block_chunk_last_block_number_cache.get(key)
        if last_block_number is not None:
            return last_block_number

        for block in self._yield_blocks_from_file(file_path, -1):
            block_chunk_last_block_number_cache[key] = last_block_number = block.get_block_number()
            break

        return last_block_number

    def _get_block_chunk_file_path_meta_enhanced(self, file_path):
        meta = get_block_chunk_file_path_meta(file_path)
        if meta is None:
            return None

        if meta.end is not None:
            return meta

        return meta._replace(end=self._get_block_chunk_last_block_number(file_path))
