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


def setdefault_if_not_none(dict_, key, value):
    if value is not None:
        dict_.setdefault(key, value)


class NodeClient:
    _instance = None

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            cls._instance = instance = cls()

        return instance

    @staticmethod
    def http_get(network_address, resource, *, parameters=None, should_raise=True):
        # We do not use reverse() because client must be framework agnostic
        url = urljoin(network_address, f'/api/v1/{resource}/')
        if parameters:
            url += '?' + urlencode(parameters)

        try:
            response = requests.get(url)
        except Exception:
            logger.warning('Could not GET %s', url, exc_info=True)
            if should_raise:
                raise
            else:
                return None

        if should_raise:
            response.raise_for_status()
        else:
            status_code = response.status_code
            if status_code != requests.codes.ok:
                logger.warning('Could not GET %s: HTTP%s: %s', url, status_code, response.text)
                return None

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            if should_raise:
                raise
            else:
                logger.warning('Non-JSON response GET %s: %s', url, response.text, exc_info=True)
                return None

        return data

    def list_resource(
        self,
        network_address,
        resource,
        *,
        offset=None,
        limit=None,
        ordering=None,
        parameters=None,
        should_raise=True
    ):
        parameters = parameters or {}
        setdefault_if_not_none(parameters, 'offset', offset)
        setdefault_if_not_none(parameters, 'limit', limit)
        setdefault_if_not_none(parameters, 'ordering', ordering)
        return self.http_get(network_address, resource, parameters=parameters, should_raise=should_raise)

    def get_latest_blockchain_state_meta_by_network_address(self, network_address) -> Optional[dict]:
        data = self.list_resource(
            network_address, 'blockchain-states-meta', limit=1, ordering='-last_block_number', should_raise=False
        )

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

    def list_block_chunks_meta_by_network_address(
        self, network_address, from_block_number=None, to_block_number=None, offset=None, limit=None, direction=1
    ):
        assert direction in (1, -1)
        parameters = {}
        setdefault_if_not_none(parameters, 'from_block_number', from_block_number)
        setdefault_if_not_none(parameters, 'to_block_number', to_block_number)

        data = self.list_resource(
            network_address,
            'block-chunks-meta',
            offset=offset,
            limit=limit,
            ordering='start_block_number' if direction == 1 else '-start_block_number',
            parameters=parameters,
            should_raise=False
        )
        return None if data is None else data['results']

    def get_latest_block_chunk_meta_by_network_address(self, network_address) -> Optional[dict]:
        results = self.list_block_chunks_meta_by_network_address(network_address, limit=1, direction=-1)
        return results[0] if results else None

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

    def yeild_blocks_from_block_chunk(self):
        raise NotImplementedError
