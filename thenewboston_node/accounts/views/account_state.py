from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from thenewboston_node.business_logic.blockchain.base import BlockchainBase

from ..serializers.account_state import AccountStateSerializer


class AccountStateViewSet(ViewSet):

    # TODO(dmu) LOW: Are there better ways to generate correct documentation?
    @extend_schema(
        responses=AccountStateSerializer,
        parameters=[OpenApiParameter('id', str, OpenApiParameter.PATH, description='Account number')],
    )
    def retrieve(self, request, pk=None):
        # TODO(dmu) MEDIUM: There is a room for performance optimization use something like `?fields=` to
        #                   retrieval of unneeded fields using get_account_balance() and
        #                   get_account_balance_lock() directly.
        #                   Also see `drf-flex-fields` and `django-restql`.
        assert pk is not None

        blockchain = BlockchainBase.get_instance()
        serializer = AccountStateSerializer(blockchain.get_account_state(pk))
        return Response(serializer.data)
