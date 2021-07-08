from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.models import Node


class NodeSerializer(DataclassSerializer):

    class Meta:
        dataclass = Node
