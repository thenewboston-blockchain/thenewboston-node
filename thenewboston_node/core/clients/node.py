import json
import logging
from typing import Optional, Type, TypeVar
from urllib.request import urlopen

from django.utils.http import urlencode

import requests
from rest_framework.reverse import reverse

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import BlockchainState
from thenewboston_node.business_logic.utils.blockchain_state import read_blockchain_state_file_from_source
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)

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
        url = '%s%s?%s' % (
            network_address.rstrip('/'),
            reverse('blockchain-states-meta-list'),
            urlencode({
                'limit': 1,
                'ordering': 'desc'
            }),
        )
        response = requests.get(url)

        if response.status_code != requests.codes.ok:
            logger.warning(
                'Unable to read blockchain state meta from %s with status_code %s', url, response.status_code
            )
            return None

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            logger.warning('Blockchain state meta response from %s is not JSON data', url, exc_info=True)
            return None

        if data.get('count') < 1:
            logger.debug('Blockchain state meta response from %s is empty', url)
            return None

        return data['results'][0]

    def get_latest_blockchain_state_binary_by_network_address(self, network_address) -> Optional[tuple[bytes, str]]:
        meta = self.get_latest_blockchain_state_meta_by_network_address(network_address)
        if meta is None:
            return None

        for url in meta['urls']:
            logger.debug('Trying to get blockchain state binary from %s', url)
            try:
                with urlopen(url) as fo:
                    return fo.read(), url
            except IOError:
                logger.warning('Unable to read blockchain state from %s', url, exc_info=True)
                continue

        return None

    def get_latest_blockchain_state_by_network_address(self, network_address) -> Optional[BlockchainState]:
        meta = self.get_latest_blockchain_state_meta_by_network_address(network_address)
        if meta is None:
            return None

        for url in meta['urls']:
            try:
                return read_blockchain_state_file_from_source(url)
            except IOError:
                logger.warning('Unable to read blockchain state from %s', url, exc_info=True)
                continue

        return None

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
