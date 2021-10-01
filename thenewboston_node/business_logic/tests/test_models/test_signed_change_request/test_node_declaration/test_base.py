import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest
from thenewboston_node.core.utils.types import hexstr


def test_can_create_node_declaration_signed_change_request(user_account_key_pair):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['127.0.0.1'],
        fee_amount=3,
        fee_account=hexstr('be10aa7e'),
        signing_key=user_account_key_pair.private
    )
    assert request
    assert request.signer
    assert request.signature
    assert request.message
    assert request.message.node.network_addresses == ['127.0.0.1']
    assert request.message.node.fee_amount == 3
    assert request.message.node.fee_account == 'be10aa7e'


def test_node_declaration_signed_change_request_validate_empty_network_address(
    user_account_key_pair, memory_blockchain
):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[], fee_amount=3, fee_account=hexstr('be10aa7e'), signing_key=user_account_key_pair.private
    )
    request.validate(memory_blockchain, block_number=0)


@pytest.mark.parametrize(
    'network_address', [
        'http://127.0.0.1',
        'http://127.0.0.1:8080',
        'http://[2001:db8::123.123.123.123]:80',
        'http://xn--d1acufc.xn--p1ai',
        'http://example.com',
        'https://my.domain.com',
        'https://my.domain.com/path/to/resource#fragment',
        'http://non-existing-localhost:8555/',
    ]
)
def test_node_declaration_signed_change_request_valid_network_addresses(
    user_account_key_pair, network_address, memory_blockchain
):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[network_address],
        fee_amount=3,
        fee_account=hexstr('be10aa7e'),
        signing_key=user_account_key_pair.private
    )
    request.validate(memory_blockchain, block_number=0)


def test_node_declaration_signed_change_request_validate_empty_hostname(user_account_key_pair, memory_blockchain):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://'],
        fee_amount=3,
        fee_account=hexstr('be10aa7e'),
        signing_key=user_account_key_pair.private
    )
    with pytest.raises(ValidationError, match='Node network_addresses hostname must be not empty'):
        request.validate(memory_blockchain, block_number=0)


def test_node_declaration_signed_change_request_validate_network_addresses_scheme(
    user_account_key_pair, memory_blockchain
):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['ftp://my.domain.com/'],
        fee_amount=3,
        fee_account=hexstr('be10aa7e'),
        signing_key=user_account_key_pair.private
    )
    with pytest.raises(ValidationError, match='Node network_addresses scheme must be one of http, https'):
        request.validate(memory_blockchain, block_number=0)


def test_node_declaration_signed_change_request_validate_empty_scheme(user_account_key_pair, memory_blockchain):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['my.domain.com/'],
        fee_amount=3,
        fee_account=hexstr('be10aa7e'),
        signing_key=user_account_key_pair.private
    )
    with pytest.raises(ValidationError, match='Node network_addresses scheme must be not empty'):
        request.validate(memory_blockchain, block_number=0)


@pytest.mark.parametrize('network_addresses', ['', None])
def test_node_declaration_signed_change_request_validate_empty_network_addresses(
    user_account_key_pair, network_addresses, memory_blockchain
):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[network_addresses],
        fee_amount=3,
        fee_account=hexstr('be10aa7e'),
        signing_key=user_account_key_pair.private
    )

    with pytest.raises(ValidationError, match='Node network_addresses must be not empty'):
        request.validate(memory_blockchain, block_number=0)


def test_node_declaration_signed_change_request_validate_negative_fee_amount(user_account_key_pair, memory_blockchain):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[], fee_amount=-3, fee_account=hexstr('be10aa7e'), signing_key=user_account_key_pair.private
    )
    with pytest.raises(ValidationError, match='Node fee_amount must be greater or equal to 0'):
        request.validate(memory_blockchain, block_number=0)


@pytest.mark.parametrize('fee_amount', [0, 3])
def test_node_declaration_signed_change_request_validate_fee_amount(
    user_account_key_pair, fee_amount, memory_blockchain
):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[],
        fee_amount=fee_amount,
        fee_account=hexstr('be10aa7e'),
        signing_key=user_account_key_pair.private
    )
    request.validate(memory_blockchain, block_number=0)


def test_node_declaration_signed_change_request_validate_fee_account_type(user_account_key_pair, memory_blockchain):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[], fee_amount=3, fee_account=1, signing_key=user_account_key_pair.private
    )
    with pytest.raises(ValidationError, match='Node fee_account must be string'):
        request.validate(memory_blockchain, block_number=0)


def test_node_declaration_signed_change_request_validate_fee_account_is_hexadecimal(
    user_account_key_pair, memory_blockchain
):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=[],
        fee_amount=3,
        fee_account=hexstr('non-hexadecimal'),
        signing_key=user_account_key_pair.private
    )
    with pytest.raises(ValidationError, match='Node fee_account must be hexadecimal string'):
        request.validate(memory_blockchain, block_number=0)
