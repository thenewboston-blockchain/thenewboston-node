from rest_framework import fields, serializers

from thenewboston_node.blockchain.serializers.block import BlockSerializer


class BlockConfirmationSerializer(serializers.Serializer):
    block = BlockSerializer()
    confirmation_signer = fields.CharField()
    confirmation_signature = fields.CharField()
