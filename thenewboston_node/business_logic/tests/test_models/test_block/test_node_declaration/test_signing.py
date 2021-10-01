from datetime import datetime
from hashlib import sha3_256

from django.conf import settings

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.models import (
    Block, Node, NodeDeclarationSignedChangeRequest, NodeDeclarationSignedChangeRequestMessage
)
from thenewboston_node.business_logic.utils.blockchain_state import BlockchainStateBuilder
from thenewboston_node.core.utils.cryptography import generate_signature
from thenewboston_node.core.utils.types import hexstr

PUBLIC = hexstr('a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12')
PRIVATE = hexstr('237fd05644605c558e79b22b0dc53e1b1d398aadf6ef10d3cc51b4fa0dc9498f')
FEE_ACCOUNT = hexstr('87051e63fc227b256b80822c53299597fab89cbd6ce3fce1d3d01db8f9a4ce74')
PV_PUBLIC = hexstr('3c8e114b7a2d8b4690b7118136575216a6d202d7aa36508b26331de0fb36c5f1')
PV_PRIVATE = hexstr('d2af8d5c53418b0a15b801561afd040af6726883541e12556bf42fe6377549f8')
NETWORK_ADDRESS = 'http://test-signing.non-existing-domain:8555/'


def make_blockchain(blockchain_directory):
    builder = BlockchainStateBuilder()
    builder.set_primary_validator(
        Node(
            identifier=PV_PUBLIC, fee_amount=4, network_addresses=['http://pv-test-signing.non-existing-domain:8555/']
        ), 0, 99
    )

    blockchain = FileBlockchain(
        base_directory=blockchain_directory,
        blockchain_state_storage_kwargs={
            'use_atomic_write': not settings.FASTER_UNITTESTS,
            'compressors': ('gz',)
        },
        block_chunk_storage_kwargs={
            'use_atomic_write': not settings.FASTER_UNITTESTS,
            'compressors': ('gz',)
        },
    )
    blockchain.add_blockchain_state(builder.get_blockchain_state())
    blockchain.utcnow = lambda: datetime(2021, 10, 1, 18, 8, 22, 834211)
    return blockchain


def test_node_declaration_block_signing_all_attributes_set(blockchain_directory):
    node = Node(
        identifier=PUBLIC,
        network_addresses=[NETWORK_ADDRESS],
        fee_amount=3,
        fee_account=FEE_ACCOUNT,
    )
    message = NodeDeclarationSignedChangeRequestMessage(node=node)

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(message, PRIVATE)
    blockchain = make_blockchain(blockchain_directory)
    block = Block.create_from_signed_change_request(blockchain, request, PV_PRIVATE)

    expected_normalized_for_cryptography = (
        b'{'
        b'"block_identifier":"9164785c082479cb2211f39ae6ad0785c642c44abff5935b921da6b547311945",'
        b'"block_number":0,'
        b'"block_type":"nd",'
        b'"signed_change_request":'
        b'{'
        b'"message":'
        b'{'
        b'"node":'
        b'{'
        b'"fee_account":"87051e63fc227b256b80822c53299597fab89cbd6ce3fce1d3d01db8f9a4ce74",'
        b'"fee_amount":3,'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'},'
        b'"signature":"8797afc6bade9ed3b5119f04bd53243a71ec26921eb2eaa5476e66aba2cd9b9b2e57110ebf788561ce'
        b'aafeb8086d5f6580b4a6a303e453dcf4c18464fb084302",'
        b'"signer":"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12"'
        b'},'
        b'"timestamp":"2021-10-01T18:08:22.834211",'
        b'"updated_account_states":'
        b'{'
        b'"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12":'
        b'{'
        b'"node":'
        b'{'
        b'"fee_account":"87051e63fc227b256b80822c53299597fab89cbd6ce3fce1d3d01db8f9a4ce74",'
        b'"fee_amount":3,'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'}'
        b'}'
        b'}'
    )
    assert block.message.get_normalized_for_cryptography() == expected_normalized_for_cryptography
    assert block.signature == generate_signature(PV_PRIVATE, expected_normalized_for_cryptography)
    assert block.hash == sha3_256(expected_normalized_for_cryptography).digest().hex()


def test_node_declaration_block_signing_all_fee_account_is_none(blockchain_directory):
    node = Node(
        identifier=PUBLIC,
        network_addresses=[NETWORK_ADDRESS],
        fee_amount=3,
        fee_account=None,
    )
    message = NodeDeclarationSignedChangeRequestMessage(node=node)

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(message, PRIVATE)
    blockchain = make_blockchain(blockchain_directory)
    block = Block.create_from_signed_change_request(blockchain, request, PV_PRIVATE)

    expected_normalized_for_cryptography = (
        b'{'
        b'"block_identifier":"9164785c082479cb2211f39ae6ad0785c642c44abff5935b921da6b547311945",'
        b'"block_number":0,'
        b'"block_type":"nd",'
        b'"signed_change_request":'
        b'{'
        b'"message":'
        b'{'
        b'"node":'
        b'{'
        b'"fee_amount":3,'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'},'
        b'"signature":"8ff178e5e3f16f4a80df93c3d37ff522660b6781ae7899a11761916c066315d3acd6b7ffcfe06d2ced179d'
        b'e222c0431b1c216f4bd2e10cda0ec0614d36ad9900",'
        b'"signer":"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12"'
        b'},'
        b'"timestamp":"2021-10-01T18:08:22.834211",'
        b'"updated_account_states":'
        b'{'
        b'"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12":'
        b'{'
        b'"node":'
        b'{'
        b'"fee_amount":3,'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'}'
        b'}'
        b'}'
    )
    assert block.message.get_normalized_for_cryptography() == expected_normalized_for_cryptography
    assert block.signature == generate_signature(PV_PRIVATE, expected_normalized_for_cryptography)
    assert block.hash == sha3_256(expected_normalized_for_cryptography).digest().hex()


def test_node_declaration_block_signing_all_fee_account_fee_account_equals_to_identifier(blockchain_directory):
    node = Node(
        identifier=PUBLIC,
        network_addresses=[NETWORK_ADDRESS],
        fee_amount=3,
        fee_account=PUBLIC,
    )
    message = NodeDeclarationSignedChangeRequestMessage(node=node)

    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(message, PRIVATE)
    blockchain = make_blockchain(blockchain_directory)
    block = Block.create_from_signed_change_request(blockchain, request, PV_PRIVATE)

    expected_normalized_for_cryptography = (
        b'{'
        b'"block_identifier":"9164785c082479cb2211f39ae6ad0785c642c44abff5935b921da6b547311945",'
        b'"block_number":0,'
        b'"block_type":"nd",'
        b'"signed_change_request":'
        b'{'
        b'"message":'
        b'{'
        b'"node":'
        b'{'
        b'"fee_amount":3,'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'},'
        b'"signature":"8ff178e5e3f16f4a80df93c3d37ff522660b6781ae7899a11761916c066315d3acd6b7ffcfe06d2ced179d'
        b'e222c0431b1c216f4bd2e10cda0ec0614d36ad9900",'
        b'"signer":"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12"'
        b'},'
        b'"timestamp":"2021-10-01T18:08:22.834211",'
        b'"updated_account_states":'
        b'{'
        b'"a8fd5acea9125fd34e63524f41ec45d2e5669bc3316b2f0c43f023145d8f4d12":'
        b'{'
        b'"node":'
        b'{'
        b'"fee_amount":3,'
        b'"network_addresses":["http://test-signing.non-existing-domain:8555/"]'
        b'}'
        b'}'
        b'}'
        b'}'
    )
    assert block.message.get_normalized_for_cryptography() == expected_normalized_for_cryptography
    assert block.signature == generate_signature(PV_PRIVATE, expected_normalized_for_cryptography)
    assert block.hash == sha3_256(expected_normalized_for_cryptography).digest().hex()
