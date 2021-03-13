import pytest

from thenewboston_node.core.utils.cryptography import generate_key_pair


@pytest.fixture
def user_account_keys():
    return generate_key_pair()
