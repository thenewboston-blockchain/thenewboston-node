from thenewboston_node.business_logic.models import (
    Node, NodeDeclarationSignedChangeRequest, NodeDeclarationSignedChangeRequestMessage
)
from thenewboston_node.core.utils.cryptography import generate_signature
from thenewboston_node.core.utils.types import hexstr

PUBLIC = hexstr('a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12')
PRIVATE = hexstr('237fd05644605c558e79b22b0dc53e1b1d398aadf6ef10d3cc51b4fa0dc9498f')
FEE_ACCOUNT = hexstr('87051e63fc227b256b80822c53299597fab89cbd6ce3fce1d3d01db8f9a4ce74')
NETWORK_ADDRESS = 'http://test-signing.non-existing-domain:8555/'


def test_node_declaration_signed_change_request_signing_all_attributes():
    node = Node(
        identifier=PUBLIC,
        network_addresses=[NETWORK_ADDRESS],
        fee_amount=3,
        fee_account=FEE_ACCOUNT,
    )
    message = NodeDeclarationSignedChangeRequestMessage(node=node)

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(message, PRIVATE)
    expected_normalized_for_cryptography = (
        b'{'
        b'"node":'
        b'{'
        b'"fee_account":"87051e63fc227b256b80822c53299597fab89cbd6ce3fce1d3d01db8f9a4ce74",'
        b'"fee_amount":3,'
        b'"identifier":"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12",'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'}'
    )
    assert request.message.get_normalized_for_cryptography() == expected_normalized_for_cryptography
    assert request.signature == generate_signature(PRIVATE, expected_normalized_for_cryptography)


def test_node_declaration_signed_change_request_signing_fee_account_is_none():
    node = Node(
        identifier=PUBLIC,
        network_addresses=[NETWORK_ADDRESS],
        fee_amount=3,
        fee_account=None,
    )
    message = NodeDeclarationSignedChangeRequestMessage(node=node)

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(message, PRIVATE)
    expected_normalized_for_cryptography = (
        b'{'
        b'"node":'
        b'{'
        b'"fee_amount":3,'
        b'"identifier":"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12",'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'}'
    )
    assert request.message.get_normalized_for_cryptography() == expected_normalized_for_cryptography
    assert request.signature == generate_signature(PRIVATE, expected_normalized_for_cryptography)


def test_node_declaration_signed_change_request_signing_fee_account_equals_to_identifier():
    node = Node(
        identifier=PUBLIC,
        network_addresses=[NETWORK_ADDRESS],
        fee_amount=3,
        fee_account=PUBLIC,
    )
    message = NodeDeclarationSignedChangeRequestMessage(node=node)

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(message, PRIVATE)
    expected_normalized_for_cryptography = (
        b'{'
        b'"node":'
        b'{'
        b'"fee_amount":3,'
        b'"identifier":"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12",'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'}'
    )
    assert request.message.get_normalized_for_cryptography() == expected_normalized_for_cryptography
    assert request.signature == generate_signature(PRIVATE, expected_normalized_for_cryptography)
