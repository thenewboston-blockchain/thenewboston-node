from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.blockchain.models import PendingBlock
from thenewboston_node.blockchain.serializers.mixins import DataclassDeserializeMixin, DataclassSerializeMixin
from thenewboston_node.blockchain.tasks.block_confirmation import start_send_block_confirmations
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import Block


class BlockSerializer(DataclassSerializeMixin, DataclassDeserializeMixin, DataclassSerializer):

    class Meta:
        dataclass = Block

    def create(self, validated_data):
        block = super().create(validated_data)
        _, is_created = PendingBlock.objects.get_or_create_for_block(block)
        # TODO(dmu) CRITICAL: Run a task to process pending block
        # TODO(dmu) CRITICAL: Remove simple adding to the blockchain after implementation of
        #                     https://github.com/thenewboston-developers/thenewboston-node/issues/461

        if is_created:
            BlockchainBase.get_instance().add_block(block)
            # TODO(dmu) CRITICAL: Send confirmations only after actually adding block to the blockchain:
            #                     https://github.com/thenewboston-developers/thenewboston-node/issues/461
            start_send_block_confirmations(block.get_block_number())

        return block
