import logging
import os.path
import shutil
from typing import Optional

import filelock
from cachetools import LRUCache

from thenewboston_node.business_logic.storages.path_optimized_file_system import PathOptimizedFileSystemStorage
from thenewboston_node.core.logging import timeit_method
from thenewboston_node.core.utils.file_lock import lock_method

from ..base import BlockchainBase
from .base import EXPECTED_LOCK_EXCEPTION, LOCKED_EXCEPTION, FileBlockchainBaseMixin  # noqa: I101
from .block_chunk.base import BlockChunkFileBlockchainMixin
from .blockchain_state.base import BlockchainStateFileBlockchainMixin

logger = logging.getLogger(__name__)


def copytree_safe(source, destination):
    if os.path.exists(source):
        shutil.copytree(source, destination)


class FileBlockchain(
    BlockChunkFileBlockchainMixin, BlockchainStateFileBlockchainMixin, FileBlockchainBaseMixin, BlockchainBase
):

    def __init__(
        self,
        *,
        base_directory,

        # Blockchain states
        blockchain_state_subdirectory='blockchain-states',
        blockchain_state_storage_kwargs=None,
        blockchain_state_cache_size=128,

        # Blocks
        block_chunk_subdirectory='block-chunks',
        block_chunk_storage_kwargs=None,
        block_cache_size=None,

        # Misc
        snapshot_period_in_blocks=100,
        block_number_digits_count=20,
        lock_filename='file.lock',
        **kwargs
    ):
        if not os.path.isabs(base_directory):
            raise ValueError('base_directory must be an absolute path')

        super().__init__(**dict(kwargs, snapshot_period_in_blocks=snapshot_period_in_blocks))

        # Blockchain states
        self._blockchain_state_directory = os.path.join(base_directory, blockchain_state_subdirectory)
        self._blockchain_state_subdirectory = blockchain_state_subdirectory
        self._blockchain_state_storage = None
        self._blockchain_state_storage_kwargs = blockchain_state_storage_kwargs
        self._blockchain_state_cache_size = blockchain_state_cache_size
        self._blockchain_state_cache: Optional[LRUCache] = None

        # Block chunks (blocks)
        self._block_chunk_directory = os.path.join(base_directory, block_chunk_subdirectory)
        self._block_chunk_subdirectory = block_chunk_subdirectory
        self._block_chunk_storage = None
        self._block_chunk_storage_kwargs = block_chunk_storage_kwargs
        self._block_cache_size = block_cache_size
        self._block_cache: Optional[LRUCache] = None

        self._block_chunk_last_block_number_cache: Optional[LRUCache] = None
        self._block_number_digits_count = block_number_digits_count

        # Common
        self._base_directory = base_directory
        self._file_lock = None
        self._lock_filename = lock_filename
        self._lock_cache = {}

    # Common
    def get_base_directory(self):
        return self._base_directory

    def get_block_number_digits_count(self):
        return self._block_number_digits_count

    @property
    def file_lock(self):
        file_lock = self._file_lock
        if file_lock is None:
            base_directory = self.get_base_directory()
            os.makedirs(base_directory, exist_ok=True)
            lock_file_path = os.path.join(base_directory, self._lock_filename)
            self._file_lock = file_lock = filelock.FileLock(lock_file_path, timeout=0)

        return file_lock

    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def clear(self):
        self._clear_locked()

    @lock_method(lock_attr='file_lock', exception=EXPECTED_LOCK_EXCEPTION)
    def _clear_locked(self):
        self.clear_caches()

        # Clear blocks
        self.get_block_chunk_storage().clear()
        self.get_block_chunk_last_block_number_cache().clear()

        # Clear blockchain states
        self.get_blockchain_state_storage().clear()

        # TODO(dmu) HIGH: Clear lock file

    def clear_caches(self):
        self.get_block_cache().clear()
        self.get_blockchain_state_cache().clear()

    # Blockchain state methods
    def get_blockchain_states_subdirectory(self):
        return self._blockchain_state_subdirectory

    def get_blockchain_state_directory(self):
        return self._blockchain_state_directory

    def get_blockchain_state_storage(self):
        if (storage := self._blockchain_state_storage) is None:
            self._blockchain_state_storage = storage = PathOptimizedFileSystemStorage(
                base_path=self._blockchain_state_directory, **(self._blockchain_state_storage_kwargs or {})
            )

        return storage

    def get_blockchain_state_cache(self):
        if (cache := self._blockchain_state_cache) is None:
            self._blockchain_state_cache = cache = LRUCache(self._blockchain_state_cache_size)

        return cache

    # Blocks methods
    def get_block_chunk_subdirectory(self):
        return self._block_chunk_subdirectory

    @timeit_method()
    def get_block_chunk_last_block_number_cache(self):
        if (cache := self._block_chunk_last_block_number_cache) is None:
            self._block_chunk_last_block_number_cache = cache = LRUCache(2)

        return cache

    def get_block_chunk_storage(self):
        if (storage := self._block_chunk_storage) is None:
            self._block_chunk_storage = storage = PathOptimizedFileSystemStorage(
                base_path=self._block_chunk_directory, **(self._block_chunk_storage_kwargs or {})
            )

        return storage

    def get_block_cache(self):
        if (cache := self._block_cache) is None:
            self._block_cache = cache = LRUCache(
                # We do not really need to cache more than `snapshot_period_in_blocks` blocks since
                # we use use account root file as a base
                self.snapshot_period_in_blocks * 2 if self._block_cache_size is None else self._block_cache_size
            )

        return cache

    @timeit_method(logger=logger, level=logging.INFO)
    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def copy_from(self, blockchain: BlockchainBase):
        if not isinstance(blockchain, FileBlockchain):
            super().copy_from(blockchain)
            return

        with blockchain.file_lock:
            self._clear_locked()
            # TODO(dmu) MEDIUM: Consider a hard-linking copying (except for incomplete block chunks, since they are
            #                   being written) for even faster copying and consuming less space
            copytree_safe(
                blockchain.get_blockchain_state_storage().base_path,
                self.get_blockchain_state_storage().base_path
            )
            copytree_safe(blockchain.get_block_chunk_storage().base_path, self.get_block_chunk_storage().base_path)
