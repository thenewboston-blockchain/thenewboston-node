import logging
import os.path
from typing import Any, Callable, Generator, Union, cast

from more_itertools import ilen

from thenewboston_node.business_logic.blockchain.file_blockchain.base import (  # noqa: I101
    EXPECTED_LOCK_EXCEPTION, LOCKED_EXCEPTION, FileBlockchainBaseMixin
)
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.core.logging import timeit_method
from thenewboston_node.core.utils.file_lock import ensure_locked, lock_method

from .meta import get_blockchain_state_filename_meta
from .misc import BLOCKCHAIN_STATE_FILENAME_TEMPLATE, LAST_BLOCK_NUMBER_NONE_SENTINEL

logger = logging.getLogger(__name__)


class BlockchainStateFileBlockchainMixin(FileBlockchainBaseMixin):

    def get_blockchain_state_storage(self):
        raise NotImplementedError('Must be implemented in child class')

    def get_blockchain_state_cache(self):
        raise NotImplementedError('Must be implemented in child class')

    def get_blockchain_state_directory(self):
        raise NotImplementedError('Must be implemented in child class')

    def make_blockchain_state_filename(self, last_block_number):
        # We need to zfill LAST_BLOCK_NUMBER_NONE_SENTINEL to maintain the nested structure of directories
        prefix_base = LAST_BLOCK_NUMBER_NONE_SENTINEL if last_block_number in (None, -1) else str(last_block_number)
        return BLOCKCHAIN_STATE_FILENAME_TEMPLATE.format(
            last_block_number=prefix_base.zfill(self.get_block_number_digits_count())
        )

    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def add_blockchain_state(self, blockchain_state: BlockchainState):
        return super().add_blockchain_state(blockchain_state)  # type: ignore

    @timeit_method()
    @ensure_locked(lock_attr='file_lock', exception=EXPECTED_LOCK_EXCEPTION)
    def persist_blockchain_state(self, blockchain_state: BlockchainState):
        filename = self.make_blockchain_state_filename(blockchain_state.last_block_number)
        self.get_blockchain_state_storage().save(filename, blockchain_state.to_messagepack(), is_final=True)

    @timeit_method(verbose_args=True)
    def _load_blockchain_state(self, filename):
        cache = self.get_blockchain_state_cache()
        blockchain_state = cache.get(filename)

        if blockchain_state is not None:
            return blockchain_state

        storage = self.get_blockchain_state_storage()
        assert storage.is_finalized(filename)
        blockchain_state = BlockchainState.from_messagepack(storage.load(filename))

        absolute_file_path = storage.get_optimized_absolute_actual_path(filename)

        base_directory = self.get_base_directory()
        assert absolute_file_path.startswith(base_directory)

        storage_base_path = str(storage.base_path)
        assert absolute_file_path.startswith(storage_base_path)

        meta = get_blockchain_state_filename_meta(
            absolute_file_path=absolute_file_path,
            blockchain_root_relative_file_path=absolute_file_path.removeprefix(base_directory).lstrip('/'),
            storage_relative_file_path=absolute_file_path.removeprefix(storage_base_path).lstrip('/'),
            base_filename=filename,
            blockchain=self,
        )

        blockchain_state.meta = meta._asdict()
        cache[filename] = blockchain_state

        return blockchain_state

    def _yield_blockchain_states(
        self,
        direction,
        lazy=False
    ) -> Generator[Union[BlockchainState, Callable[[Any], BlockchainState]], None, None]:
        assert direction in (1, -1)

        for file_path in self.get_blockchain_state_storage().list_directory(sort_direction=direction):
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

    def get_blockchain_state_count(self) -> int:
        return ilen(self.get_blockchain_state_storage().list_directory())

    def _get_blockchain_state_real_file_path(self, file_path):
        optimized_path = self.get_blockchain_state_storage().get_optimized_path(file_path)
        abs_optimized_path = os.path.join(self.get_blockchain_state_directory(), optimized_path)
        return os.path.relpath(abs_optimized_path, self.get_base_directory())

    @lock_method(lock_attr='file_lock', exception=LOCKED_EXCEPTION)
    def snapshot_blockchain_state(self):
        block_chunk_filename = self.get_current_block_chunk_filename()
        last_block_number = self.get_last_block_number()
        blockchain_state = super().snapshot_blockchain_state()
        if blockchain_state:
            self.finalize_block_chunk(block_chunk_filename, last_block_number)

        self.finalize_all_block_chunks()
