from rest_framework.serializers import SerializerMethodField
from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import Node


class NodeSerializer(DataclassSerializer):

    role = SerializerMethodField()

    class Meta:
        dataclass = Node

    def get_role(self, node):
        node_role = BlockchainBase.get_instance().get_node_role(identifier=node.identifier)

        if node_role is None:
            return None

        return node_role.value
