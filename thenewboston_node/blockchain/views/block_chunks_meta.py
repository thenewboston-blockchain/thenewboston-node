from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.blockchain.serializers.block_chunks_meta import BlockChunksMetaSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.core.exceptions import NotImplementAPIError
from thenewboston_node.core.filters import (
    AdvanceIteratorFilterSet, AdvanceIteratorNumberFilter, SingleFieldReversibleOrderingFilter
)
from thenewboston_node.core.pagination import CustomNoCountLimitOffsetPagination
from thenewboston_node.core.utils.itertools import AdvancedIterator


class BlockChunksMetaFilterSet(AdvanceIteratorFilterSet):
    from_block_number = AdvanceIteratorNumberFilter(lambda x, filter_value: x.end_block_number >= filter_value)
    to_block_number = AdvanceIteratorNumberFilter(lambda x, filter_value: x.start_block_number <= filter_value)

    class Meta:
        model = None
        fields = ('from_block_number', 'to_block_number')


class BlockChunksMetaViewSet(ListModelMixin, GenericViewSet):
    serializer_class = BlockChunksMetaSerializer
    pagination_class = CustomNoCountLimitOffsetPagination
    filter_backends = (SingleFieldReversibleOrderingFilter, DjangoFilterBackend)
    filterset_class = BlockChunksMetaFilterSet
    ordering_fields = ('start_block_number',)

    def get_queryset(self):
        blockchain = BlockchainBase.get_instance()
        if not isinstance(blockchain, FileBlockchain):
            raise NotImplementAPIError(f'End-point is not available for {blockchain.__class__.__name__}')

        return AdvancedIterator(
            source=blockchain.yield_block_chunks_meta(),
            reversed_source=blockchain.yield_block_chunks_meta(direction=-1),
        )
