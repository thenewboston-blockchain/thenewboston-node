from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.models.signed_change_request import NodeDeclarationSignedChangeRequest


class NodeDeclarationSignedChangeRequestSerializer(DataclassSerializer):

    class Meta:
        dataclass = NodeDeclarationSignedChangeRequest

    def to_internal_value(self, data):
        return NodeDeclarationSignedChangeRequest.deserialize_from_dict(data)
