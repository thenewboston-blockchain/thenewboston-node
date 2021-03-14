import pytest

from thenewboston_node.core.utils.cryptography import KeyPair, generate_key_pair


@pytest.fixture
def user_account_key_pair() -> KeyPair:
    return generate_key_pair()


@pytest.fixture
def node_key_pair() -> KeyPair:
    return generate_key_pair()


@pytest.fixture
def primary_validator_key_pair() -> KeyPair:
    return generate_key_pair()


@pytest.fixture
def treasury_account_key_pair() -> KeyPair:
    return KeyPair(
        '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
        '1104d51eb539e66fa108f99d18ab179aa98c10678961821ddd87bfdbf351cb79',
    )
