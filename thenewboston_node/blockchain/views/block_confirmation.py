from rest_framework import mixins
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from thenewboston_node.blockchain import serializers
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.exceptions import ValidationError


class BlockConfirmationViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = serializers.BlockConfirmationSerializer

    def perform_create(self, serializer):
        confirmation_request = serializer.validated_data

        blockchain = BlockchainBase.get_instance()
        try:
            blockchain.add_block(confirmation_request['block'])
        except ValidationError as ex:
            raise DRFValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(ex)]})
