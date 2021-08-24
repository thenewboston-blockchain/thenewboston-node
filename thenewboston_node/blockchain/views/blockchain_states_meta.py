from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.viewsets import ReadOnlyModelViewSet

from thenewboston_node.blockchain.serializers.blockchain_states_meta import BlockchainStatesMetaSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.core.pagination import CustomLimitOffsetPagination
from thenewboston_node.core.utils.itertools import SliceableCountableIterable

GENESIS_BLOCKCHAIN_STATE_IDS = ('null', 'genesis')


class BlockchainStatesMetaViewSet(ReadOnlyModelViewSet):
    serializer_class = BlockchainStatesMetaSerializer
    pagination_class = CustomLimitOffsetPagination

    @extend_schema(
        parameters=[
            OpenApiParameter('id', location=OpenApiParameter.PATH, description="Block number or 'null' or 'genesis'")
        ]
    )
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
            return SliceableCountableIterable(
                blockchain.yield_blockchain_states(lazy=True), count=blockchain.get_blockchain_states_count
            )
        elif ordering == 'desc':
            return SliceableCountableIterable(
                blockchain.yield_blockchain_states_reversed(lazy=True), count=blockchain.get_blockchain_states_count
            )
        else:
            raise ParseError("ordering query parameter must be 'asc' or 'desc'")

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        block_number = self.kwargs[lookup_url_kwarg].strip()
        if block_number in GENESIS_BLOCKCHAIN_STATE_IDS:
            block_number = -1

        try:
            block_number = int(block_number)
        except (ValueError, TypeError):
            raise NotFound()

        blockchain = BlockchainBase.get_instance()
        try:
            blockchain_state = blockchain.get_blockchain_state_by_block_number(
                block_number=block_number, inclusive=block_number != -1
            )
        except ValueError:
            raise NotFound()

        if blockchain_state.get_last_block_number() == block_number:
            return blockchain_state
        raise NotFound()
