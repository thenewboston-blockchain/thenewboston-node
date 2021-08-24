import logging
import os.path
from typing import Any, Callable, Generator, Optional, Union, cast

import filelock
from cachetools import LRUCache
from more_itertools import ilen

from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.business_logic.storages.path_optimized_file_system import PathOptimizedFileSystemStorage
from thenewboston_node.core.utils.file_lock import ensure_locked, lock_method

from ..base import BlockchainBase
from .base import EXPECTED_LOCK_EXCEPTION, LOCKED_EXCEPTION, FileBlockchainBaseMixin  # noqa: I101
from .block_chunk import BlockChunkFileBlockchainMixin
from .blockchain_state import get_blockchain_state_filename_meta, make_blockchain_state_filename

logger = logging.getLogger(__name__)

DEFAULT_BLOCK_CHUNK_SIZE = 100


class FileBlockchain(BlockChunkFileBlockchainMixin, FileBlockchainBaseMixin, BlockchainBase):

    def __init__(
        self,
        *,
        base_directory,

        # Blockchain states
        blockchain_states_subdirectory='blockchain-states',
        account_root_files_cache_size=128,
        account_root_files_storage_kwargs=None,

        # Blocks
        block_chunk_subdirectory='block-chunks',
        block_chunk_storage_kwargs=None,
        block_chunk_size=DEFAULT_BLOCK_CHUNK_SIZE,
        block_cache_size=None,

        # Misc
        block_number_digits_count=20,
        lock_filename='file.lock',
        **kwargs
    ):
        if not os.path.isabs(base_directory):
            raise ValueError('base_directory must be an absolute path')

        kwargs.setdefault('snapshot_period_in_blocks', block_chunk_size)
        super().__init__(**kwargs)

        # Blockchain states
        blockchain_states_directory = os.path.join(base_directory, blockchain_states_subdirectory)
        self.blockchain_states_storage = PathOptimizedFileSystemStorage(
            base_path=blockchain_states_directory, **(account_root_files_storage_kwargs or {})
        )
        self._blockchain_states_subdirectory = blockchain_states_subdirectory
        self._blockchain_states_directory = blockchain_states_directory

        # Block chunks (blocks)
        self._block_chunk_directory = os.path.join(base_directory, block_chunk_subdirectory)
        self._block_chunk_subdirectory = block_chunk_subdirectory
        self._block_chunk_storage = None
        self._block_chunk_storage_kwargs = block_chunk_storage_kwargs
        self._block_chunk_size = block_chunk_size
        self._block_cache_size = block_cache_size
        self._block_cache: Optional[LRUCache] = None

        # Misc
        self._base_directory = base_directory

        self.account_root_files_cache_size = account_root_files_cache_size

        self.blockchain_states_cache: Optional[LRUCache] = None
        self.block_chunk_last_block_number_cache: Optional[LRUCache] = None
        self.initialize_caches()

        self._file_lock = None
        self.lock_filename = lock_filename

        # self._blockchain_states_storage_directory_max_depth = block_chunk_size
        self._block_number_digits_count = block_number_digits_count

    # Common
    def get_base_directory(self):
        return self._base_directory

    def get_block_number_digits_count(self):
        return self._block_number_digits_count

    def get_block_chunk_size(self):
        return self._block_chunk_size

    @property
    def file_lock(self):
        file_lock = self._file_lock
        if file_lock is None:
            base_directory = self.get_base_directory()
            os.makedirs(base_directory, exist_ok=True)
            lock_file_path = os.path.join(base_directory, self.lock_filename)
            self._file_lock = file_lock = filelock.FileLock(lock_file_path, timeout=0)

        return file_lock

    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def clear(self):
        self.initialize_caches()
        self.get_block_cache().clear()
        self.get_block_chunk_storage().clear()
        self.blockchain_states_storage.clear()
        # TODO(dmu) HIGH: Clear lock file

    def initialize_caches(self):
        self.blockchain_states_cache = LRUCache(self.account_root_files_cache_size)
        self.block_chunk_last_block_number_cache = LRUCache(2)

    # Blockchain state methods
    def get_blockchain_states_subdirectory(self):
        return self._blockchain_states_subdirectory

    def make_blockchain_state_filename(self, last_block_number):
        return make_blockchain_state_filename(last_block_number, self.get_block_number_digits_count())

    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def add_blockchain_state(self, blockchain_state: BlockchainState):
        return super().add_blockchain_state(blockchain_state)

    @ensure_locked(lock_attr='file_lock', exception=EXPECTED_LOCK_EXCEPTION)
    def persist_blockchain_state(self, blockchain_state: BlockchainState):
        filename = self.make_blockchain_state_filename(blockchain_state.get_last_block_number())
        self.blockchain_states_storage.save(filename, blockchain_state.to_messagepack(), is_final=True)

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
        abs_optimized_path = os.path.join(self._blockchain_states_directory, optimized_path)
        return os.path.relpath(abs_optimized_path, self.get_base_directory())

    # Blocks methods
    def get_block_chunks_subdirectory(self):
        return self._block_chunk_subdirectory

    def get_block_chunk_last_block_number_cache(self):
        return self.block_chunk_last_block_number_cache

    def get_block_chunk_storage(self):
        if (block_chunk_storage := self._block_chunk_storage) is None:
            self._block_chunk_storage = block_chunk_storage = PathOptimizedFileSystemStorage(
                base_path=self._block_chunk_directory, **(self._block_chunk_storage_kwargs or {})
            )

        return block_chunk_storage

    def get_block_cache(self):
        if (block_cache := self._block_cache) is None:
            self._block_cache = block_cache = LRUCache(
                # We do not really need to cache more than `snapshot_period_in_blocks` blocks since
                # we use use account root file as a base
                self.snapshot_period_in_blocks * 2 if self._block_cache_size is None else self._block_cache_size
            )

        return block_cache
