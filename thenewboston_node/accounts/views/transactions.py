from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.accounts.filters import TransactionOrderingFilter
from thenewboston_node.accounts.serializers.transaction import TransactionSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.core.pagination import CustomNoCountLimitOffsetPagination
from thenewboston_node.core.utils.itertools import SliceableReversableCountableIterable


class TransactionViewSet(ListModelMixin, GenericViewSet):
    serializer_class = TransactionSerializer
    pagination_class = CustomNoCountLimitOffsetPagination
    filter_backends = (TransactionOrderingFilter,)

    def get_queryset(self):
        account_id = self.kwargs.get('id')
        blockchain = BlockchainBase.get_instance()

        return SliceableReversableCountableIterable(
            source=blockchain.yield_transactions(account_id=account_id),
            reversed_source=blockchain.yield_transactions(account_id=account_id, is_reversed=True)
        )
