from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.models.signed_change_request_message import CoinTransferTransaction


class TransactionSerializer(DataclassSerializer):

    class Meta:
        dataclass = CoinTransferTransaction
