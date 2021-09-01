from thenewboston_node.business_logic.models import (
    AccountState, Block, BlockchainState, Node, NodeDeclarationSignedChangeRequest
)
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.tests import factories
from thenewboston_node.business_logic.tests.baker_factories import baker


def test_node_serializes_with_identifier_standalone():
    node = baker.make(Node)
    assert node.identifier
    serialized = node.serialize_to_dict()
    assert 'identifier' in serialized
    assert serialized['identifier'] == node.identifier


def test_node_serializes_with_identifier_in_account_state():
    node = baker.make(Node)
    assert node.identifier

    account_state = AccountState(node=node)
    serialized = account_state.serialize_to_dict()
    assert 'identifier' in serialized['node']
    assert serialized['node']['identifier'] == node.identifier


def test_node_serializes_without_identifier_in_blockchain_state():
    node = baker.make(Node)
    account_number = node.identifier
    assert account_number
    account_state = AccountState(node=node)
    blockchain_state = factories.BlockchainStateFactory(
        message=factories.BlockchainStateMessageFactory(account_states={account_number: account_state})
    )

    serialized = blockchain_state.serialize_to_dict()
    assert 'identifier' not in serialized['message']['account_states'][account_number]['node']

    deserialized = BlockchainState.deserialize_from_dict(serialized)
    deserialized_node = deserialized.account_states[account_number].node
    assert deserialized_node is not node
    assert deserialized_node.identifier == account_number


def test_node_serializes_without_identifier_in_block(memory_blockchain, user_account_key_pair):
    account_number = user_account_key_pair.public
    node = baker.make(Node, identifier=account_number)

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.34:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    block = Block.create_from_signed_change_request(memory_blockchain, request, get_node_signing_key())

    serialized = block.serialize_to_dict()
    assert 'identifier' not in serialized['message']['updated_account_states'][account_number]['node']

    deserialized = Block.deserialize_from_dict(serialized)
    deserialized_node = deserialized.message.updated_account_states[account_number].node
    assert deserialized_node is not node
    assert deserialized_node.identifier == account_number
