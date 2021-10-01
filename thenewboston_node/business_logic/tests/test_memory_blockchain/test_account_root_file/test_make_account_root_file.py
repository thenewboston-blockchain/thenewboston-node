from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models.block import Block


def test_can_make_blockchain_state_on_last_block(
    file_blockchain: BlockchainBase, blockchain_genesis_state, treasury_account_key_pair, user_account_key_pair,
    primary_validator, preferred_node, primary_validator_key_pair, confirmation_validator
):
    blockchain = file_blockchain

    assert blockchain.get_number_of_accounts() == 3

    user_account = user_account_key_pair.public
    treasury_account = treasury_account_key_pair.public
    treasury_initial_balance = blockchain.get_account_current_balance(treasury_account)
    assert treasury_initial_balance is not None

    retrieved_blockchain_state = blockchain.get_last_blockchain_state()
    retrieved_blockchain_state.meta = None
    assert retrieved_blockchain_state == blockchain_genesis_state

    retrieved_blockchain_state = blockchain.get_blockchain_state_by_block_number(-1)
    retrieved_blockchain_state.meta = None
    assert blockchain.get_blockchain_state_by_block_number(-1) == blockchain_genesis_state

    assert blockchain_genesis_state.account_states[treasury_account].get_balance_lock(
        treasury_account
    ) == treasury_account
    assert blockchain.get_blockchain_state_count() == 1

    blockchain.snapshot_blockchain_state()
    assert blockchain.get_blockchain_state_count() == 1

    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=30,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block0)

    assert blockchain.get_number_of_accounts() == 5  # treasure, user, node, pv, cv

    blockchain.snapshot_blockchain_state()
    assert blockchain.get_blockchain_state_count() == 2
    blockchain.snapshot_blockchain_state()
    assert blockchain.get_blockchain_state_count() == 2

    blockchain_state = blockchain.get_last_blockchain_state()
    assert blockchain_state is not None
    assert blockchain_state.last_block_number == 0
    assert blockchain_state.last_block_identifier == block0.message.block_identifier
    assert blockchain_state.next_block_identifier == block0.hash

    account_states = blockchain_state.account_states
    assert len(account_states) == 5
    assert account_states.keys() == {
        user_account, treasury_account, primary_validator.identifier, preferred_node.identifier,
        confirmation_validator.identifier
    }
    assert account_states[user_account].balance == 30
    assert account_states[user_account].balance_lock is None
    assert account_states[user_account].get_balance_lock(user_account) == user_account

    assert account_states[treasury_account].balance == treasury_initial_balance - 30 - 4 - 1
    assert account_states[treasury_account].balance_lock != treasury_account

    assert account_states[primary_validator.identifier].balance == 4
    assert account_states[primary_validator.identifier].balance_lock is None
    assert account_states[primary_validator.identifier].get_balance_lock(
        primary_validator.identifier
    ) == primary_validator.identifier

    assert account_states[preferred_node.identifier].balance == 1
    assert account_states[preferred_node.identifier].balance_lock is None
    assert account_states[preferred_node.identifier].get_balance_lock(
        preferred_node.identifier
    ) == preferred_node.identifier

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=treasury_account,
        amount=20,
        request_signing_key=user_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block1)

    block2 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=primary_validator.identifier,
        amount=2,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block2)

    blockchain.snapshot_blockchain_state()
    blockchain_state = blockchain.get_last_blockchain_state()

    assert blockchain_state is not None
    assert blockchain_state.last_block_number == 2
    assert blockchain_state.last_block_identifier == block2.message.block_identifier
    assert blockchain_state.next_block_identifier == block2.hash

    account_states = blockchain_state.account_states
    assert len(account_states) == 5
    assert account_states.keys() == {
        user_account, treasury_account, primary_validator.identifier, preferred_node.identifier,
        confirmation_validator.identifier
    }
    assert account_states[user_account].balance == 5
    assert account_states[user_account].balance_lock != user_account

    assert account_states[treasury_account].balance == treasury_initial_balance - 30 - 4 - 1 + 20 - 2 - 4 - 1
    assert account_states[treasury_account].balance_lock != treasury_account

    assert account_states[primary_validator.identifier].balance == 4 + 4 + 4 + 2
    assert account_states[primary_validator.identifier].balance_lock is None
    assert account_states[primary_validator.identifier].get_balance_lock(
        primary_validator.identifier
    ) == primary_validator.identifier

    assert account_states[preferred_node.identifier].balance == 1 + 1 + 1
    assert account_states[preferred_node.identifier].balance_lock is None
    assert account_states[preferred_node.identifier].get_balance_lock(
        preferred_node.identifier
    ) == preferred_node.identifier
