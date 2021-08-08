from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ParseError
from rest_framework.viewsets import ReadOnlyModelViewSet

from thenewboston_node.blockchain.serializers.blockchain_states_meta import BlockchainStatesMetaSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.core.pagination import CustomLimitOffsetPagination


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
        blockchain = BlockchainBase.get_instance()

        ordering = self.request.query_params.get('ordering', 'asc')
        if ordering == 'asc':
            return list(blockchain.yield_blockchain_states())
        elif ordering == 'desc':
            return list(blockchain.yield_blockchain_states_reversed())
        else:
            raise ParseError("ordering query parameter must be 'asc' or 'desc'")

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        block_number = self.kwargs[lookup_url_kwarg]
        try:
            block_number = int(block_number)
        except (ValueError, TypeError):
            raise ParseError('Block number must be integer')

        if block_number < -1:
            raise ParseError('Block number must be >= -1')

        blockchain = BlockchainBase.get_instance()
        return blockchain.get_blockchain_state_by_block_number(block_number=block_number)
