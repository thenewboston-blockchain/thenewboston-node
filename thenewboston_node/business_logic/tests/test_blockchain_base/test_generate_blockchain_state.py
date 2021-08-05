from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.node import get_node_signing_key


def test_can_generate_blockchain_state(file_blockchain, treasury_account_key_pair, user_account, treasury_initial_balance, preferred_node):
    treasury_account = treasury_account_key_pair.public
    blockchain = file_blockchain

    block_0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=99,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
        preferred_node=preferred_node,
    )
    file_blockchain.add_block(block_0)

    blockchain_state = blockchain.generate_blockchain_state()

    assert blockchain_state.message.account_states[user_account].balance == 99
    assert blockchain_state.message.account_states[treasury_account].balance == treasury_initial_balance - 99 - 4 - 1
