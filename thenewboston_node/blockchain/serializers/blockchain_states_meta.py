import os.path
from urllib.parse import urljoin

from django.conf import settings

from rest_framework import fields

from thenewboston_node.business_logic.node import get_node_identifier
from thenewboston_node.core.exceptions import ClientSideAPIError
from thenewboston_node.core.serializers import CustomSerializer


def make_url_path(blockchain_state):
    file_path = (blockchain_state.meta or {}).get('file_path')
    return os.path.join(settings.BLOCKCHAIN_URL_PATH_PREFIX, file_path) if file_path else None


class BlockchainStatesMetaSerializer(CustomSerializer):
    last_block_number = fields.IntegerField(source='message.last_block_number')
    url_path = fields.SerializerMethodField()
    urls = fields.SerializerMethodField()

    def get_url_path(self, blockchain_state):
        return make_url_path(blockchain_state)

    def get_urls(self, blockchain_state):
        url_path = make_url_path(blockchain_state)
        if url_path is None:
            return None

        blockchain = (blockchain_state.meta or {}).get('blockchain')
        if blockchain is None:
            return None

        this_node = blockchain.get_node_by_identifier(get_node_identifier())
        if this_node is None:
            raise ClientSideAPIError('Requested node is unregistered in the blockchain')

        return [urljoin(net_address, url_path) for net_address in this_node.network_addresses]
