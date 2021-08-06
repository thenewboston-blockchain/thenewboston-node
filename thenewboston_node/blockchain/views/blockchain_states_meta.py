from urllib.parse import urljoin

from django.conf import settings

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import APIException, ParseError
from rest_framework.viewsets import ReadOnlyModelViewSet

from thenewboston_node.blockchain import exceptions
from thenewboston_node.blockchain.pagination import CustomLimitOffsetPagination
from thenewboston_node.blockchain.serializers.blockchain_states_meta import BlockchainStatesMetaSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.models import BlockchainState
from thenewboston_node.business_logic.node import get_node_identifier


class BlockchainStatesMetaViewSet(ReadOnlyModelViewSet):
    serializer_class = BlockchainStatesMetaSerializer
    pagination_class = CustomLimitOffsetPagination

    @extend_schema(parameters=[OpenApiParameter('id', location=OpenApiParameter.PATH, description='Block number')])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter('ordering', location=OpenApiParameter.QUERY, description='asc/desc', default='asc'),
        ]
    )
    def list(self, request):  # noqa: A003
        return super().list(request)

    def get_queryset(self):
        blockchain = self._get_blockchain()
        blockchain_states = self._get_blockchain_states(blockchain)
        return [
            self._make_blockchain_state_meta(blockchain, blockchain_state) for blockchain_state in blockchain_states
        ]

    def get_object(self):
        blockchain = self._get_blockchain()
        blockchain_state = blockchain.get_blockchain_state_by_block_number(block_number=self._get_block_number())
        return self._make_blockchain_state_meta(blockchain, blockchain_state)

    def _get_blockchain_states(self, blockchain):
        ordering = self.request.query_params.get('ordering', 'asc')
        if ordering == 'asc':
            blockchain_states = blockchain.yield_blockchain_states()
        elif ordering == 'desc':
            blockchain_states = blockchain.yield_blockchain_states_reversed()
        else:
            raise ParseError("ordering query parameter must be 'asc' or 'desc'")
        return blockchain_states

    def _get_block_number(self):
        try:
            block_number = int(self.kwargs['pk'])
        except KeyError:
            raise ParseError('Block number is not provided')
        except ValueError:
            raise ParseError('Block number must be integer')
        if block_number < -1:
            raise ParseError('Block number must be >= -1')
        return block_number

    @staticmethod
    def _make_blockchain_state_meta(blockchain, blockchain_state: BlockchainState):
        meta = blockchain_state.meta or {}
        try:
            file_path = meta['file_path']
        except KeyError:
            raise APIException('Blockchain state file path not found')
        url_path = urljoin(settings.BLOCKCHAIN_URL_PATH_PREFIX, file_path)

        this_node = blockchain.get_node_by_identifier(get_node_identifier())
        if this_node is None:
            raise APIException('Requested node is unregistered in the blockchain')

        return {
            'last_block_number': blockchain_state.last_block_number,
            'url_path': url_path,
            'urls': [urljoin(net_address, url_path) for net_address in this_node.network_addresses],
        }

    @staticmethod
    def _get_blockchain():
        blockchain = BlockchainBase.get_instance()
        if not isinstance(blockchain, FileBlockchain):
            raise exceptions.APINotImplemented()
        return blockchain
