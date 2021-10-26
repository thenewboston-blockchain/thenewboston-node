import json
import logging
from functools import partial
from typing import Generator, Optional, Type, TypeVar
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen

import requests

from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain.sources import URLBlockSource
from thenewboston_node.business_logic.utils.blockchain_state import read_blockchain_state_file_from_source
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='NodeClient')


def setdefault_if_not_none(dict_, key, value):
    if value is not None:
        dict_.setdefault(key, value)


def requests_get(url, *args, **kwargs):
    # We need this function to mock it easier for unittests
    return requests.get(url, *args, **kwargs)


def requests_post(url, *args, **kwargs):
    # We need this function to mock it easier for unittests
    return requests.post(url, *args, **kwargs)


class NodeClient:
    _instance = None

    def __init__(self):
        self.http_get = partial(self._call_requests_func, requests_get)
        self.http_post = partial(self._call_requests_func, requests_post)

    @classmethod
    def get_instance(cls: Type[T]) -> T:
        instance = cls._instance
        if not instance:
            instance = cls()
            cls.set_instance_cache(instance)

        return instance

    @classmethod
    def set_instance_cache(cls: Type[T], instance: T):
        cls._instance = instance

    @classmethod
    def clear_instance_cache(cls):
        cls._instance = None

    @staticmethod
    def _call_requests_func(
        requests_func, network_address, resource, *, payload=None, parameters=None, should_raise=True
    ):
        # We do not use reverse() because client must be framework agnostic
        url = urljoin(network_address, f'/api/v1/{resource}/')
        if parameters:
            url += '?' + urlencode(parameters)
        addition_arguments = dict(json=payload) if payload else {}
        try:
            response = requests_func(url, **addition_arguments)
        except Exception:
            logger.warning('Could not call %s', url, exc_info=True)
            if should_raise:
                raise
            else:
                return None

        if should_raise:
            response.raise_for_status()
        else:
            status_code = response.status_code
            if status_code != requests.codes.ok:
                logger.warning('Could not call %s: HTTP%s: %s', url, status_code, response.text)
                return None

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            if should_raise:
                raise
            else:
                logger.warning('Non-JSON response call %s: %s', url, response.text, exc_info=True)
                return None

        return data

    def _list_resource(
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
        data = self._list_resource(
            network_address, 'blockchain-states-meta', limit=1, ordering='-last_block_number', should_raise=False
        )
        if not data:
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

    def get_latest_blockchain_state_by_network_address(self, network_address) -> Optional[models.BlockchainState]:
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

        data = self._list_resource(
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
            return block_chunk_meta['end_block_number']

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

    def yield_blocks_slice(self, network_address, from_block_number: int,
                           to_block_number: int) -> Generator[models.Block, None, None]:
        # TODO(dmu) MEDIUM: Consider improvements for network failovers
        # by the moment of downloading the last (incomplete) block chunk its name may change
        # (because of becoming complete) therefore we retry
        last_block_number = None
        for _ in range(2):
            block_chunks = self.list_block_chunks_meta_by_network_address(
                network_address, from_block_number=from_block_number, to_block_number=to_block_number
            )
            if block_chunks is None:
                logger.warning('Returned None as block_chunks')
                continue

            for block_chunk in block_chunks:
                # TODO(dmu) HIGH: Support download from more than one URL
                url = block_chunk['urls'][0]
                source = URLBlockSource(url)
                try:
                    source.force_read()
                except Exception:
                    logger.warning('Error trying to download %s', url)
                    break

                for block in URLBlockSource(url):
                    block_number = block.get_block_number()
                    if from_block_number is not None and block_number < from_block_number:
                        # TODO(dmu) LOW: This can be optimized by applying the codition only to first block chunk
                        #                (be careful first block chunk may be also the last)
                        # skip not requested block
                        continue

                    if last_block_number is not None and block_number <= last_block_number:
                        # TODO(dmu) LOW: This maybe excessive precaution
                        # We have seen this block already
                        continue

                    if to_block_number is not None and to_block_number < block_number:
                        return

                    yield block
                    last_block_number = block_number

            if last_block_number is None:
                continue

            assert to_block_number is None or last_block_number <= to_block_number
            if to_block_number is not None and last_block_number >= to_block_number:  # defensive programming
                break

            from_block_number = last_block_number + 1

    def send_signed_change_request_by_network_address(
        self, network_address, signed_change_request: models.SignedChangeRequest
    ):
        logger.debug('Sending %s to %s', signed_change_request, network_address)
        payload = signed_change_request.serialize_to_dict()
        return self.http_post(network_address, 'signed-change-requests', payload=payload)

    def send_signed_change_request_to_node(self, node: models.Node, signed_change_request: models.SignedChangeRequest):
        for network_address in node.network_addresses:
            try:
                self.send_signed_change_request_by_network_address(network_address, signed_change_request)
                return
            except requests.ConnectionError:
                pass
        else:
            raise ConnectionError(f'Could not send signed change request to {node}')

    def send_block_confirmation_by_network_address(
        self, *, network_address, block: models.Block, confirmation_signer, confirmation_signature
    ):
        logger.debug('Sending %s confirmation to %s', block, network_address)
        payload = {
            'block': block.serialize_to_dict(),
            'confirmation_signer': confirmation_signer,
            'confirmation_signature': confirmation_signature,
        }
        return self.http_post(network_address, 'block-confirmations', payload)

    def send_block_confirmation_to_node(
        self, *, node: models.Node, block: models.Block, confirmation_signer, confirmation_signature
    ):
        for network_address in node.network_addresses:
            try:
                self.send_block_confirmation_by_network_address(
                    network_address=network_address,
                    block=block,
                    confirmation_signer=confirmation_signer,
                    confirmation_signature=confirmation_signature,
                )
                return
            except requests.ConnectionError:
                pass
        else:
            raise ConnectionError(f'Could not send block confirmation to {node}')
