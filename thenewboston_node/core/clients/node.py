from typing import Optional, Type, TypeVar

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.core.utils.types import hexstr

T = TypeVar('T', bound='NodeClient')


class NodeClient:
    _instance = None

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            cls._instance = instance = cls()

        return instance

    def get_latest_blockchain_state_meta_by_network_address(self, network_address) -> Optional[dict]:
        # TODO(dmu) CRITICAL: Unmock this method once this task is done:
        #                     https://github.com/thenewboston-developers/thenewboston-node/issues/252
        return {
            'last_block_number':
                None,
            'path':
                '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-arf.msgpack.xz',
            'urls': [
                'http://3.143.205.184:8555/blockchain/blockchain-states/0/0/0/0/0/0/0/0/000000000!-arf.msgpack.xz'
            ]
        }

    def get_latest_blockchain_state_meta_by_network_addresses(self, network_addresses) -> Optional[dict]:
        for network_address in network_addresses:
            # TODO(dmu) CRITICAL: Try another network_address only if this one is unavailable
            return self.get_latest_blockchain_state_meta_by_network_address(network_address)

        return None

    def get_latest_blockchain_state_meta_by_node_identifier(self, blockchain: BlockchainBase,
                                                            node_identifier: hexstr) -> Optional[dict]:
        node = blockchain.get_node_by_identifier(node_identifier)
        if node is None:
            return None

        network_addresses = node.network_addresses
        if not network_addresses:
            return None

        return self.get_latest_blockchain_state_meta_by_network_addresses(network_addresses)
