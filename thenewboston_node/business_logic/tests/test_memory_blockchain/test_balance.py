from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.core.utils.cryptography import KeyPair


def test_get_account_state_from_blockchain_genesis_state(
    memory_blockchain: MemoryBlockchain, treasury_account_key_pair: KeyPair, blockchain_genesis_state: BlockchainState
):
    account = treasury_account_key_pair.public
    assert memory_blockchain.get_account_current_balance(account) == 281474976710656
    assert memory_blockchain.get_account_current_balance(account
                                                         ) == blockchain_genesis_state.get_account_balance(account)


def test_can_get_account_state_by_block_number(
    memory_blockchain: MemoryBlockchain, treasury_account_key_pair: KeyPair, user_account_key_pair: KeyPair,
    primary_validator, preferred_node, primary_validator_key_pair
):

    blockchain = memory_blockchain
    sender = treasury_account_key_pair.public
    recipient = user_account_key_pair.public
    total_fees = primary_validator.fee_amount + preferred_node.fee_amount

    sender_initial_balance = blockchain.get_account_current_balance(sender)
    assert sender_initial_balance == 281474976710656
    assert blockchain.get_account_balance(sender, -1) == sender_initial_balance
    assert blockchain.get_account_balance(recipient, -1) == 0
    assert blockchain.get_account_current_balance(recipient) == 0

    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=recipient,
        amount=10,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block0)
    assert blockchain.get_account_balance(sender, -1) == sender_initial_balance
    assert blockchain.get_account_balance(recipient, -1) == 0
    assert blockchain.get_account_balance(sender, 0) == sender_initial_balance - 10 - total_fees
    assert blockchain.get_account_balance(recipient, 0) == 10
    assert blockchain.get_account_current_balance(sender) == sender_initial_balance - 10 - total_fees
    assert blockchain.get_account_current_balance(recipient) == 10

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=recipient,
        amount=11,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block1)
    assert blockchain.get_account_balance(sender, -1) == sender_initial_balance
    assert blockchain.get_account_balance(recipient, -1) == 0
    assert blockchain.get_account_balance(sender, 0) == sender_initial_balance - 10 - total_fees
    assert blockchain.get_account_balance(recipient, 0) == 10
    assert blockchain.get_account_balance(sender, 1) == sender_initial_balance - 10 - 11 - 2 * total_fees
    assert blockchain.get_account_balance(recipient, 1) == 10 + 11
    assert blockchain.get_account_current_balance(sender) == sender_initial_balance - 10 - 11 - 2 * total_fees
    assert blockchain.get_account_current_balance(recipient) == 10 + 11

    block2 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=recipient,
        amount=12,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block2)
    assert blockchain.get_account_balance(sender, -1) == sender_initial_balance
    assert blockchain.get_account_balance(recipient, -1) == 0
    assert blockchain.get_account_balance(sender, 0) == sender_initial_balance - 10 - total_fees
    assert blockchain.get_account_balance(recipient, 0) == 10
    assert blockchain.get_account_balance(sender, 1) == sender_initial_balance - 10 - 11 - 2 * total_fees
    assert blockchain.get_account_balance(recipient, 1) == 10 + 11
    assert blockchain.get_account_balance(sender, 2) == sender_initial_balance - 10 - 11 - 12 - 3 * total_fees
    assert blockchain.get_account_balance(recipient, 2) == 10 + 11 + 12
    assert blockchain.get_account_current_balance(sender) == sender_initial_balance - 10 - 11 - 12 - 3 * total_fees
    assert blockchain.get_account_current_balance(recipient) == 10 + 11 + 12
