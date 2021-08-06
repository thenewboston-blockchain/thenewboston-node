from rest_framework import fields, serializers


class BlockchainStatesMetaSerializer(serializers.Serializer):
    last_block_number = fields.IntegerField()
    url_path = fields.CharField()
    urls = fields.ListField(fields.CharField())
