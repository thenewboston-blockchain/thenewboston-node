from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from thenewboston_node.accounts.serializers.node import NodeSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.node import get_node_identifier
from thenewboston_node.core.pagination import CustomLimitOffsetPagination
from thenewboston_node.core.utils.itertools import SliceableCountableIterable
from thenewboston_node.core.utils.types import hexstr

PRIMARY_VALIDATOR_NODE_ID = 'pv'
SELF_NODE_ID = 'self'

PK_DESCRIPTION = f"Node identifier or '{SELF_NODE_ID}' or '{PRIMARY_VALIDATOR_NODE_ID}'"


class NodeViewSet(ReadOnlyModelViewSet):
    serializer_class = NodeSerializer
    pagination_class = CustomLimitOffsetPagination

    @extend_schema(parameters=[OpenApiParameter('id', location=OpenApiParameter.PATH, description=PK_DESCRIPTION)])
    def retrieve(self, request, pk: str = None):
        assert pk is not None
        blockchain = BlockchainBase.get_instance()

        node_id = hexstr(pk.lower())
        if node_id == PRIMARY_VALIDATOR_NODE_ID:
            node = blockchain.get_primary_validator()
        elif node_id == SELF_NODE_ID:
            node = blockchain.get_node_by_identifier(identifier=get_node_identifier())
        else:
            node = blockchain.get_node_by_identifier(identifier=node_id)

        if node is None:
            raise NotFound(detail='Node not found')

        serializer = self.serializer_class(node)
        return Response(serializer.data)

    def get_queryset(self):
        blockchain = BlockchainBase.get_instance()
        return SliceableCountableIterable(blockchain.yield_nodes(), count=blockchain.get_nodes_count)
