from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.blockchain.serializers.signed_change_request import NodeDeclarationSignedChangeRequestSerializer
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.node import get_node_identifier, get_node_signing_key
from thenewboston_node.core.clients.node import NodeClient


class SignedChangeRequestViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = NodeDeclarationSignedChangeRequestSerializer

    def perform_create(self, serializer):
        signed_change_request = serializer.save()

        blockchain = BlockchainBase.get_instance()

        if blockchain.get_node_role(get_node_identifier()) == NodeRole.PRIMARY_VALIDATOR:
            try:
                block = Block.create_from_signed_change_request(
                    blockchain,
                    signed_change_request=signed_change_request,
                    pv_signing_key=get_node_signing_key(),
                )
                blockchain.add_block(block)
            except ValidationError as ex:
                # TODO(dmu) MEDIUM: Why can't we just do `raise DRFValidationError(str(ex))` ?
                raise DRFValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(ex)]})
            # TODO(dmu) CRITICAL: Send notifications to CVs about new block
            return

        primary_validator = blockchain.get_primary_validator()
        NodeClient.get_instance().send_signed_change_request_to_node(primary_validator, signed_change_request)
