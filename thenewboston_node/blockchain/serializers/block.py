from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.blockchain.models import PendingBlock
from thenewboston_node.blockchain.serializers.mixins import DataclassDeserializeMixin, DataclassSerializeMixin
from thenewboston_node.business_logic.models import Block


class BlockSerializer(DataclassSerializeMixin, DataclassDeserializeMixin, DataclassSerializer):

    class Meta:
        dataclass = Block

    def create(self, validated_data):
        block = super().create(validated_data)
        PendingBlock.objects.get_or_create_for_block(block)
        return block
