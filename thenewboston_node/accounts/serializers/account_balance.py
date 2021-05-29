from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.models.account_state import AccountState


class AccountBalanceSerializer(DataclassSerializer):
    """
    Represents account balance state
    """

    class Meta:
        dataclass = AccountState
