import pytest

from thenewboston_node.business_logic.models import CoinTransferTransaction
from thenewboston_node.business_logic.models.transfer_request_message import TransferRequestMessage


@pytest.fixture
def sample_transfer_request_message(
    treasury_account_key_pair, user_account_key_pair, node_key_pair, primary_validator_key_pair
):
    return TransferRequestMessage(
        balance_lock=treasury_account_key_pair.public,
        txs=[
            CoinTransferTransaction(amount=10, recipient=user_account_key_pair.public),
            CoinTransferTransaction(amount=1, recipient=node_key_pair.public, fee=True),
            CoinTransferTransaction(amount=4, recipient=primary_validator_key_pair.public, fee=True),
        ]
    )
