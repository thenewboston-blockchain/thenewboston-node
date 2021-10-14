from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.blockchain.serializers.mixins import DataclassDeserializeMixin, DataclassSerializeMixin
from thenewboston_node.business_logic.models import Block


class BlockSerializer(DataclassSerializeMixin, DataclassDeserializeMixin, DataclassSerializer):

    class Meta:
        dataclass = Block
