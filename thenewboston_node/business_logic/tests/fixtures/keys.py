import pytest

from thenewboston_node.business_logic.tests.base import force_node_key
from thenewboston_node.core.utils.cryptography import KeyPair
from thenewboston_node.core.utils.types import hexstr


@pytest.fixture
def user_account_key_pair() -> KeyPair:
    return KeyPair(
        public=hexstr('97b369953f665956d47b0a003c268ad2b05cf601b8798210ca7c2423afb9af78'),
        private=hexstr('f450b3082201544bc9348e862b818d3423857c0eb7bec5d00751098424186454'),
    )


@pytest.fixture
def preferred_node_key_pair() -> KeyPair:
    return KeyPair(
        public=hexstr('1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb'),
        private=hexstr('d0a03fea134f3f83901f36071f79026b2224a7f926546486f72104351dc23432'),
    )


@pytest.fixture
def another_node_key_pair() -> KeyPair:
    return KeyPair(
        public=hexstr('e612bbaee57540dce9b17fd351fe7e4b1ad2bc916733171108dcac294886bcf5'),
        private=hexstr('a2c182ff4a7ca2343d1197f079d29aa8bd77aa8b73294c38006f5a0968e00a4e'),
    )


@pytest.fixture
def primary_validator_key_pair() -> KeyPair:
    return KeyPair(
        public=hexstr('b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1'),
        private=hexstr('98d6b2744d93245e48e336b7d24a316947005b00805c776cff9946109c194675'),
    )


@pytest.fixture
def treasury_account_key_pair() -> KeyPair:
    return KeyPair(
        public=hexstr('4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'),
        private=hexstr('1104d51eb539e66fa108f99d18ab179aa98c10678961821ddd87bfdbf351cb79'),
    )


@pytest.fixture
def user_account(user_account_key_pair):
    return user_account_key_pair.public


@pytest.fixture
def primary_validator_identifier(primary_validator_key_pair):
    return primary_validator_key_pair.public


@pytest.fixture
def node_identifier(preferred_node_key_pair):
    return preferred_node_key_pair.public


@pytest.fixture
def treasury_account(treasury_account_key_pair):
    return treasury_account_key_pair.public


@pytest.fixture
def treasury_account_signing_key(treasury_account_key_pair):
    return treasury_account_key_pair.private


@pytest.fixture
def as_primary_validator(primary_validator_key_pair):
    return force_node_key(primary_validator_key_pair.private)


@pytest.fixture
def as_regular_node(another_node_key_pair):
    return force_node_key(another_node_key_pair.private)
