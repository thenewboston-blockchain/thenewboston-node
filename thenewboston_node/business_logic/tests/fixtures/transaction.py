import pytest

from thenewboston_node.business_logic.models.transaction import Transaction


@pytest.fixture
def sample_transaction(node_key_pair):
    return Transaction(recipient=node_key_pair.public, amount=10, fee=True)
