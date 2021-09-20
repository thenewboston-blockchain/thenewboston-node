import pytest

from thenewboston_node.business_logic.tests.base import force_node_fee


@pytest.fixture(autouse=True)
def unittest_settings(as_primary_validator):
    with as_primary_validator, force_node_fee(fee_amount=4):
        yield
