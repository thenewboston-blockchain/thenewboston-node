import pytest

from thenewboston_node.business_logic.models import CoinTransferSignedRequestMessage, CoinTransferTransaction


@pytest.fixture
def sample_coin_transfer_signed_request_message(
    treasury_account_key_pair, user_account_key_pair, node_key_pair, primary_validator_key_pair
):
    return CoinTransferSignedRequestMessage(
        balance_lock=treasury_account_key_pair.public,
        txs=[
            CoinTransferTransaction(amount=10, recipient=user_account_key_pair.public),
            CoinTransferTransaction(amount=1, recipient=node_key_pair.public, fee=True),
            CoinTransferTransaction(amount=4, recipient=primary_validator_key_pair.public, fee=True),
        ]
    )
