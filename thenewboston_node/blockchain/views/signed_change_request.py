from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.blockchain.serializers.signed_change_request import NodeDeclarationSignedChangeRequestSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.node import get_node_identifier, get_node_signing_key
from thenewboston_node.core.clients.node import NodeClient


class SignedChangeRequestViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = NodeDeclarationSignedChangeRequestSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signed_change_request = serializer.save()

        blockchain = BlockchainBase.get_instance()

        if blockchain.get_node_role(get_node_identifier()) == NodeRole.PRIMARY_VALIDATOR:
            block = Block.create_from_signed_change_request(
                blockchain,
                signed_change_request=signed_change_request,
                pv_signing_key=get_node_signing_key(),
            )
            blockchain.add_block(block)

        else:
            primary_validator = blockchain.get_primary_validator()
            NodeClient.get_instance().post_signed_change_request_by_node(primary_validator, signed_change_request)

        return Response(status=status.HTTP_201_CREATED)
