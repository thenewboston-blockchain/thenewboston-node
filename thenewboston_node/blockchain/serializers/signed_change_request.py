from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.models import (
    CoinTransferSignedChangeRequest, NodeDeclarationSignedChangeRequest, SignedChangeRequest
)
from thenewboston_node.business_logic.models.base import BaseDataclass
from thenewboston_node.business_logic.models.constants import BlockType
from thenewboston_node.core.serializers import DataclassDeserializeMixin


class SignedChangeRequestMessageTypeSerializer(serializers.Serializer):
    signed_change_request_type = serializers.ChoiceField(choices=tuple(item.value for item in BlockType))


class SignedChangeRequestTypeSerializer(serializers.Serializer):
    message = SignedChangeRequestMessageTypeSerializer()


class SignedChangeRequestSerializer(DataclassDeserializeMixin, DataclassSerializer):

    def create(self, validated_data):
        if isinstance(validated_data, BaseDataclass):
            return validated_data  # not need to recreate the instance, just return it

        return super().create(validated_data)

    class Meta:
        dataclass = SignedChangeRequest


class NodeDeclarationSignedChangeRequestSerializer(SignedChangeRequestSerializer):

    class Meta(SignedChangeRequestSerializer.Meta):
        dataclass = NodeDeclarationSignedChangeRequest  # type: ignore


class CoinTransferSignedChangeRequestSerializer(SignedChangeRequestSerializer):

    class Meta(SignedChangeRequestSerializer.Meta):
        dataclass = CoinTransferSignedChangeRequest  # type: ignore
