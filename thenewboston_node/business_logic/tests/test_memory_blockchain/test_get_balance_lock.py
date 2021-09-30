from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.core.utils.cryptography import KeyPair


def test_get_account_lock(
    memory_blockchain: MemoryBlockchain,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
    preferred_node,
    primary_validator_key_pair,
):
    blockchain = memory_blockchain

    treasury_account = treasury_account_key_pair.public
    user_account = user_account_key_pair.public

    assert blockchain.get_next_block_number() == 0
    assert blockchain.get_account_current_balance_lock(treasury_account) == treasury_account
    assert blockchain.get_account_balance_lock(treasury_account, -1) == treasury_account

    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=30,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block0)
    assert blockchain.get_next_block_number() == 1

    block0_treasury_account_balance = block0.message.updated_account_states.get(treasury_account)
    assert block0_treasury_account_balance
    assert blockchain.get_account_current_balance_lock(
        treasury_account
    ) == block0_treasury_account_balance.balance_lock
    assert blockchain.get_account_balance_lock(treasury_account, -1) == treasury_account

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block1)
    assert blockchain.get_next_block_number() == 2

    block1_treasury_account_balance = block1.message.updated_account_states.get(treasury_account)
    assert block1_treasury_account_balance

    assert blockchain.get_account_current_balance_lock(
        treasury_account
    ) == block1_treasury_account_balance.balance_lock
    assert blockchain.get_account_balance_lock(treasury_account, 0) == block0_treasury_account_balance.balance_lock
    assert blockchain.get_account_balance_lock(treasury_account, -1) == treasury_account
