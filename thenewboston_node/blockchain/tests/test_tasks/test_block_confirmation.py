from thenewboston_node.blockchain.tasks.block_confirmation import send_block_confirmation
from thenewboston_node.business_logic.tests.base import as_confirmation_validator, as_regular_node, force_blockchain
from thenewboston_node.core.tests.base import force_node_client


def test_cannot_send_block_confirmation_as_regular_node(
    node_client_mock, file_blockchain_with_two_blockchain_states, another_node
):
    blockchain = file_blockchain_with_two_blockchain_states
    with force_node_client(node_client_mock), force_blockchain(blockchain), as_regular_node():
        send_block_confirmation(another_node.identifier, block_number=0)

    node_client_mock.send_block_confirmation_to_node.assert_not_called()


def test_can_send_block_confirmation_as_cv(
    node_client_mock, file_blockchain_with_two_blockchain_states, preferred_node
):
    blockchain = file_blockchain_with_two_blockchain_states
    with force_node_client(node_client_mock), force_blockchain(blockchain), as_confirmation_validator():
        send_block_confirmation(preferred_node.identifier, block_number=0)

    node_client_mock.send_block_confirmation_to_node.assert_called()
