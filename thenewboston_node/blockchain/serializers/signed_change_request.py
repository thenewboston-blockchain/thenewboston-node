from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.blockchain.serializers.mixins import DataclassDeserializeMixin
from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest


class NodeDeclarationSignedChangeRequestSerializer(DataclassDeserializeMixin, DataclassSerializer):

    class Meta:
        dataclass = NodeDeclarationSignedChangeRequest
