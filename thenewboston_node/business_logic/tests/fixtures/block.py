import pytest

from thenewboston_node.business_logic.tests import factories


@pytest.fixture
def block_0():
    return factories.CoinTransferBlockFactory(message=factories.CoinTransferBlockMessageFactory(block_number=0))


@pytest.fixture
def block_1():
    return factories.CoinTransferBlockFactory(message=factories.CoinTransferBlockMessageFactory(block_number=1))


@pytest.fixture
def block_2():
    return factories.CoinTransferBlockFactory(
        message=factories.CoinTransferBlockMessageFactory(block_number=2),
        hash='fake-message-hash',
    )
