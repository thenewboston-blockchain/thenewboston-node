import copy

from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.blockchain.serializers.block_chunks_meta import BlockChunksMetaSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.core.exceptions import NotImplementAPIError
from thenewboston_node.core.filters import SingleFieldReversibleOrderingFilter
from thenewboston_node.core.pagination import CustomNoCountLimitOffsetPagination
from thenewboston_node.core.utils.itertools import FilterableIterator


class StartBlockNumberFilter(NumberFilter):

    def filter(self, qs, value):  # noqa: A003
        if value is None:
            return qs

        # TODO(dmu) MEDIUM: Improve filtering performance to avoid traversal of unneeded items
        qs.add_filter(lambda x: x.end_block_number >= value)
        return qs


class EndBlockNumberFilter(NumberFilter):

    def filter(self, qs, value):  # noqa: A003
        if value is None:
            return qs

        # TODO(dmu) MEDIUM: Improve filtering performance to avoid traversal of unneeded items
        qs.add_filter(lambda x: x.start_block_number <= value)
        return qs


class BlockChunksMetaFilterSet(FilterSet):
    start_block_number = StartBlockNumberFilter()
    end_block_number = EndBlockNumberFilter()

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        self.is_bound = data is not None
        self.data = data or {}
        self.queryset = queryset
        self.request = request
        self.form_prefix = prefix

        self.filters = copy.deepcopy(self.base_filters)

    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)

        return queryset

    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            self._qs = self.filter_queryset(self.queryset)
        return self._qs

    class Meta:
        model = None
        fields = ('start_block_number', 'end_block_number')


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

        return FilterableIterator(
            source=blockchain.yield_block_chunks_meta(),
            reversed_source=blockchain.yield_block_chunks_meta(direction=-1),
        )
