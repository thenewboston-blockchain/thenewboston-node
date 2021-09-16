import logging
import os.path
import re
from collections import namedtuple
from typing import Any, Callable, Generator, Union, cast

from more_itertools import ilen

from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS
from thenewboston_node.core.logging import timeit_method
from thenewboston_node.core.utils.file_lock import ensure_locked, lock_method

from .base import EXPECTED_LOCK_EXCEPTION, LOCKED_EXCEPTION, FileBlockchainBaseMixin  # noqa: I101

LAST_BLOCK_NUMBER_NONE_SENTINEL = '!'
BLOCKCHAIN_STATE_FILENAME_TEMPLATE = '{last_block_number}-blockchain-state.msgpack'
BLOCKCHAIN_STATE_FILENAME_RE = re.compile(
    BLOCKCHAIN_STATE_FILENAME_TEMPLATE.format(last_block_number=r'(?P<last_block_number>\d*(?:!|\d))') +
    r'(?:|\.(?P<compression>{}))$'.format('|'.join(COMPRESSION_FUNCTIONS.keys()))
)
BlockchainFilenameMeta = namedtuple('BlockchainFilenameMeta', 'last_block_number compression')

logger = logging.getLogger(__name__)


def get_blockchain_state_filename_meta(filename):
    match = BLOCKCHAIN_STATE_FILENAME_RE.match(filename)
    if not match:
        return None

    last_block_number_str = match.group('last_block_number')

    if last_block_number_str.endswith(LAST_BLOCK_NUMBER_NONE_SENTINEL):
        last_block_number = None
    else:
        last_block_number = int(last_block_number_str)

    return BlockchainFilenameMeta(last_block_number, match.group('compression') or None)


class BlochainStateFileBlockchainMixin(FileBlockchainBaseMixin):

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
    def _load_blockchain_state(self, file_path):
        cache = self.get_blockchain_state_cache()
        blockchain_state = cache.get(file_path)

        if blockchain_state is None:
            storage = self.get_blockchain_state_storage()
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
