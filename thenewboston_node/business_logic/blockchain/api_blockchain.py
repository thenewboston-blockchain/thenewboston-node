from typing import Optional

from thenewboston_node.core.clients.node import NodeClient

from ..models import BlockchainState
from .base import BlockchainBase


# TODO(dmu) CRITICAL: Improve error handling
class APIBlockchain(BlockchainBase):

    def __init__(self, *args, **kwargs):
        self.network_address = kwargs.pop('network_address')
        super().__init__(*args, **kwargs)

    def get_last_blockchain_state_last_block_number(self) -> int:
        meta = NodeClient.get_instance().get_latest_blockchain_state_meta_by_network_address(self.network_address)
        if not meta:
            # TODO(dmu) CRITICAL: Implement handling IO errors
            raise NotImplementedError('Handling connection related issue is not implemented')

        assert meta is not None
        return meta['last_block_number']

    def get_last_blockchain_state(self) -> Optional[BlockchainState]:  # type: ignore
        return NodeClient.get_instance().get_latest_blockchain_state_by_network_address(self.network_address)

    def get_last_block_number(self) -> int:
        # TODO(dmu) CRITICAL: Implement handling IO errors
        last_block_number = NodeClient.get_instance().get_last_block_number_by_network_address(self.network_address)
        if last_block_number is None:
            return self.get_last_blockchain_state_last_block_number()

        return last_block_number

    def yield_blocks_slice(self, from_block_number: int, to_block_number: int):
        yield from NodeClient.get_instance().yield_blocks_slice(
            self.network_address, from_block_number=from_block_number, to_block_number=to_block_number
        )
