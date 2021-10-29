import logging
from typing import Generator, Optional

from cachetools import TTLCache

from thenewboston_node.core.clients.node import NodeClient

from ...core.utils.types import hexstr
from ..enums import NodeRole
from ..models import BlockchainState, Node
from .base import BlockchainBase

logger = logging.getLogger(__name__)

LIST_NODES_LIMIT = 20


class APIBlockchain(BlockchainBase):
    # TODO(dmu) CRITICAL: Improve error handling

    def __init__(self, *args, **kwargs):
        self.network_address = kwargs.pop('network_address')
        self.roles_cache = TTLCache(1000, 60)
        super().__init__(*args, **kwargs)

    def yield_nodes(self, block_number: Optional[int] = None) -> Generator[Node, None, None]:
        if block_number is not None:
            raise NotImplementedError('Support for block_number argument has not been implemented')

        network_address = self.network_address
        node_client = NodeClient.get_instance()
        offset = 0
        while True:
            response = node_client.list_nodes(network_address, offset=offset, limit=LIST_NODES_LIMIT)
            nodes = response['results']
            if not nodes:
                break

            for node_dict in nodes:
                role = node_dict.pop('role')
                node = Node.deserialize_from_dict(node_dict)

                self.roles_cache[node.identifier] = NodeRole(role)
                yield node

            offset += len(nodes)

    def get_last_blockchain_state_last_block_number(self) -> int:
        meta = NodeClient.get_instance().get_latest_blockchain_state_meta_by_network_address(self.network_address)
        if not meta:
            # TODO(dmu) CRITICAL: Implement handling IO errors
            raise NotImplementedError('Handling connection related issues is not implemented')

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

    def get_node_role(self, identifier: hexstr) -> Optional[NodeRole]:
        role = self.roles_cache.get(identifier)
        if role:
            return role

        logger.warning('Could not get role from cache')
        # TODO(dmu) MEDIUM: Refactor to make API call to get node role in case cache miss
        return super().get_node_role(identifier)
