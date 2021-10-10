from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.tests.base import as_primary_validator, as_regular_node
from thenewboston_node.business_logic.tests.factories import add_blocks


def test_can_generate_blockchain_state(
    file_blockchain, treasury_account_key_pair, user_account, treasury_initial_balance, preferred_node,
    primary_validator_key_pair
):
    treasury_account = treasury_account_key_pair.public
    blockchain = file_blockchain

    block_0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=99,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    file_blockchain.add_block(block_0)

    blockchain_state = blockchain.generate_blockchain_state()

    assert blockchain_state.account_states[user_account].balance == 99
    assert blockchain_state.account_states[treasury_account].balance == treasury_initial_balance - 99 - 4 - 1


def test_generated_blockchain_state_is_signed_if_node_is_primary_validator(file_blockchain):
    with as_primary_validator(file_blockchain):
        add_blocks(file_blockchain, 2)
        blockchain_state = file_blockchain.generate_blockchain_state()

    blockchain_state.validate_signature()
    assert blockchain_state.is_signed_by_primary_validator(file_blockchain)


def test_generated_blockchain_state_signature_is_empty_if_node_is_regular(file_blockchain, primary_validator_key_pair):
    with as_regular_node(file_blockchain):
        add_blocks(file_blockchain, 2)
        blockchain_state = file_blockchain.generate_blockchain_state()

    assert blockchain_state.signature is None
    assert blockchain_state.signer == primary_validator_key_pair.public
    assert not blockchain_state.is_signed_by_primary_validator(file_blockchain)
