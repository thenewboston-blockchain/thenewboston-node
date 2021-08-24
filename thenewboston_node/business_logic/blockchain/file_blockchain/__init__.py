import logging
import os.path
from typing import Optional

import filelock
from cachetools import LRUCache

from thenewboston_node.business_logic.storages.path_optimized_file_system import PathOptimizedFileSystemStorage
from thenewboston_node.core.utils.file_lock import lock_method

from ..base import BlockchainBase
from .base import LOCKED_EXCEPTION, FileBlockchainBaseMixin  # noqa: I101
from .block_chunk import BlockChunkFileBlockchainMixin
from .blockchain_state import BlochainStateFileBlockchainMixin

logger = logging.getLogger(__name__)

DEFAULT_BLOCK_CHUNK_SIZE = 100


class FileBlockchain(
    BlockChunkFileBlockchainMixin, BlochainStateFileBlockchainMixin, FileBlockchainBaseMixin, BlockchainBase
):

    def __init__(
        self,
        *,
        base_directory,

        # Blockchain states
        blockchain_state_subdirectory='blockchain-states',
        account_root_files_cache_size=128,
        blockchain_state_storage_kwargs=None,

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
        self._blockchain_state_directory = os.path.join(base_directory, blockchain_state_subdirectory)
        self._blockchain_state_subdirectory = blockchain_state_subdirectory
        self._blockchain_state_storage = None
        self._blockchain_state_storage_kwargs = blockchain_state_storage_kwargs
        self._blockchain_state_cache_size = account_root_files_cache_size
        self._blockchain_state_cache: Optional[LRUCache] = None

        # Block chunks (blocks)
        self._block_chunk_directory = os.path.join(base_directory, block_chunk_subdirectory)
        self._block_chunk_subdirectory = block_chunk_subdirectory
        self._block_chunk_storage = None
        self._block_chunk_storage_kwargs = block_chunk_storage_kwargs
        self._block_cache_size = block_cache_size
        self._block_cache: Optional[LRUCache] = None

        self._block_chunk_size = block_chunk_size
        self.block_chunk_last_block_number_cache: Optional[LRUCache] = None

        # Common
        self._base_directory = base_directory
        self.initialize_caches()
        self._file_lock = None
        self.lock_filename = lock_filename
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
        # Clear blocks
        self.get_block_cache().clear()
        self.get_block_chunk_storage().clear()

        # Clear blockchain states
        self.get_blockchain_state_cache().clear()
        self.get_blockchain_state_storage().clear()

        # TODO(dmu) HIGH: Clear lock file

    def initialize_caches(self):
        self.block_chunk_last_block_number_cache = LRUCache(2)

    # Blockchain state methods
    def get_blockchain_states_subdirectory(self):
        return self._blockchain_state_subdirectory

    def get_blockchain_state_directory(self):
        return self._blockchain_state_directory

    def get_blockchain_state_storage(self):
        if (blockchain_state_storage := self._blockchain_state_storage) is None:
            self._blockchain_state_storage = blockchain_state_storage = PathOptimizedFileSystemStorage(
                base_path=self._blockchain_state_directory, **(self._blockchain_state_storage_kwargs or {})
            )

        return blockchain_state_storage

    def get_blockchain_state_cache(self):
        if (blockchain_state_cache := self._blockchain_state_cache) is None:
            self._blockchain_state_cache = blockchain_state_cache = LRUCache(self._blockchain_state_cache_size)

        return blockchain_state_cache

    # Blocks methods
    def get_block_chunk_subdirectory(self):
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
