from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key


def test_last_block_data_is_correct(file_blockchain):
    blockchain_state = file_blockchain.get_last_blockchain_state()
    assert blockchain_state.last_block_number is None


def test_balances_are_correct(
    file_blockchain, treasury_account_key_pair, user_account, primary_validator_identifier, node_identifier,
    treasury_initial_balance, preferred_node
):
    blockchain = file_blockchain

    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=100,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
        preferred_node=preferred_node
    )
    blockchain.add_block(block)
    blockchain.snapshot_blockchain_state()

    pv_fee = blockchain.get_primary_validator().fee_amount
    node_fee = preferred_node.fee_amount
    assert pv_fee > 0
    assert node_fee > 0
    assert pv_fee != node_fee

    blockchain_state = file_blockchain.get_last_blockchain_state()
    assert blockchain_state
    accounts = blockchain_state.account_states

    assert len(accounts) == 4
    assert accounts[treasury_account_key_pair.public].balance == treasury_initial_balance - pv_fee - node_fee - 100
    assert accounts[user_account].balance == 100
    assert accounts[primary_validator_identifier].balance == pv_fee
    assert accounts[node_identifier].balance == node_fee
