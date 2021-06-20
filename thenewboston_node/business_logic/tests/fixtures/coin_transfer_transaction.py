import pytest

from thenewboston_node.business_logic.models import CoinTransferTransaction


@pytest.fixture
def sample_coin_transfer_transaction(node_key_pair):
    return CoinTransferTransaction(recipient=node_key_pair.public, amount=10, is_fee=True)
