from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.blockchain.serializers.block import BlockSerializer


class CreateBlockViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = BlockSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response
