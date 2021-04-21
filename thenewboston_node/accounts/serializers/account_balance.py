from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.models.account_balance import AccountBalance


class AccountBalanceSerializer(DataclassSerializer):
    """
    Represents account balance state
    """

    class Meta:
        dataclass = AccountBalance
