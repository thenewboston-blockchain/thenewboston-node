from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.blockchain.serializers.block_chunks_meta import BlockChunksMetaSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.core.exceptions import NotImplementAPIError
from thenewboston_node.core.filters import SingleFieldReversibleOrderingFilter
from thenewboston_node.core.pagination import CustomLimitOffsetPagination
from thenewboston_node.core.utils.itertools import SliceableReversibleCountableIterable


class BlockChunksMetaViewSet(ListModelMixin, GenericViewSet):
    serializer_class = BlockChunksMetaSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (SingleFieldReversibleOrderingFilter,)
    ordering_fields = ('start_block_number',)

    def get_queryset(self):
        blockchain = BlockchainBase.get_instance()
        if not isinstance(blockchain, FileBlockchain):
            raise NotImplementAPIError(f'End-point is not available for {blockchain.__class__.__name__}')

        return SliceableReversibleCountableIterable(
            source=blockchain.yield_block_chunks_meta(),
            reversed_source=blockchain.yield_block_chunks_meta(direction=-1),
            count=blockchain.get_block_chunks_count
        )
