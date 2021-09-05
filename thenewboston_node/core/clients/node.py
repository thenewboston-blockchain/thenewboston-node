import json
import logging
from typing import Optional, Type, TypeVar
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen

import requests

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
        # We do not use reverse() because client must be framework agnostic
        params = urlencode({'limit': 1, 'ordering': '-last_block_number'})
        url = urljoin(network_address, '/api/v1/blockchain-states-meta/') + '?' + params

        try:
            response = requests.get(url)
        except Exception:
            logger.warning('Could not get latest blockchain state by GET %s', url, exc_info=True)
            return None

        if response.status_code != requests.codes.ok:
            logger.warning(
                'Could not get latest blockchain state by GET %s with status_code HTTP%s: %s', url,
                response.status_code, response.text
            )
            return None

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            logger.warning('Blockchain state meta response from %s is not JSON data', url, exc_info=True)
            return None

        results = data['results']
        if not results:
            return None

        return results[0]

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

        logger.warning('Could not read latest blockchain state from node: %s', network_address)
        return None

    def get_latest_blockchain_state_meta_by_network_addresses(self, network_addresses) -> Optional[dict]:
        for network_address in network_addresses:
            # TODO(dmu) CRITICAL: Try another network_address only if this one is unavailable
            return self.get_latest_blockchain_state_meta_by_network_address(network_address)

        return None

    def get_latest_block_chunk_meta_by_network_address(self, network_address) -> Optional[dict]:
        # We do not use reverse() because client must be framework agnostic
        params = urlencode({'limit': 1, 'ordering': '-start_block_number'})
        url = urljoin(network_address, '/api/v1/block-chunks-meta/') + '?' + params

        try:
            response = requests.get(url)
        except Exception:
            logger.warning('Could not get latest block chunk by GET %s', url, exc_info=True)
            return None

        if response.status_code != requests.codes.ok:
            logger.warning(
                'Could not get latest block chunk by GET %s with status_code HTTP%s: %s', url, response.status_code,
                response.text
            )
            return None

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            logger.warning('Block chunk meta response from %s is not JSON data', url, exc_info=True)
            return None

        results = data['results']
        if not results:
            return None

        return results[0]

    def get_last_block_number_by_network_address(self, network_address):
        block_chunk_meta = self.get_latest_block_chunk_meta_by_network_address(network_address)
        if block_chunk_meta:
            raise block_chunk_meta['end_block_number']

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
