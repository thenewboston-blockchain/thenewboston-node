from typing import Optional

from thenewboston_node.core.clients.node import NodeClient

# TODO(dmu) CRITICAL: Improve error handling
from ...core.utils.types import hexstr
from ..enums import NodeRole
from ..models import BlockchainState, Node
from .base import BlockchainBase


class APIBlockchain(BlockchainBase):

    def __init__(self, *args, **kwargs):
        self.network_address = kwargs.pop('network_address')
        self.stored_roles = dict()
        super().__init__(*args, **kwargs)

    def yield_nodes(self, block_number: Optional[int] = None):
        if block_number is not None:
            raise NotImplementedError('Support for block_number argument has not been implemented')

        node_client = NodeClient.get_instance()
        offset = 0
        limit = 20
        while True:
            response = node_client.list_nodes(self.network_address, offset=offset, limit=limit)
            if not response['results']:
                break
            for _node in response['results']:
                self.stored_roles[_node['identifier']] = NodeRole(_node['role'])
                node = Node.deserialize_from_dict(_node, complain_excessive_keys=False)
                yield node
            offset += len(response['results'])

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
        role = self.stored_roles.get(identifier)
        if role is not None:
            return role
        return super().get_node_role(identifier)
