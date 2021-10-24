from thenewboston_node.blockchain.tasks.block_confirmation import send_block_confirmation, send_block_confirmations
from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.tests.base import as_confirmation_validator, force_blockchain
from thenewboston_node.core.tests.base import force_node_client


def test_can_send_block_confirmation_as_cv(
    node_client_mock, file_blockchain_with_two_blockchain_states, preferred_node
):
    blockchain = file_blockchain_with_two_blockchain_states
    with force_node_client(node_client_mock), force_blockchain(blockchain), as_confirmation_validator():
        send_block_confirmation(preferred_node.identifier, block_number=0)

    node_client_mock.send_block_confirmation_to_node.assert_called()


def test_send_block_confirmations(
    file_blockchain, preferred_node, user_account_key_pair, start_send_block_confirmation_mock
):
    blockchain = file_blockchain
    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account_key_pair.public,
        amount=10,
        request_signing_key=blockchain._test_treasury_account_key_pair.private,
        pv_signing_key=blockchain._test_primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )

    block_number = block.get_block_number()
    with force_blockchain(blockchain), as_confirmation_validator():
        send_block_confirmations(block_number=block_number)

    calls = start_send_block_confirmation_mock.call_args_list
    assert {item[1]['target_node_identifier'] for item in calls} == {blockchain._test_regular_node_key_pair.public}
    assert {item[1]['block_number'] for item in calls} == {0}
