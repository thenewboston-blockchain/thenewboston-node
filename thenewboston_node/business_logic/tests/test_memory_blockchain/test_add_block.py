import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.cryptography import KeyPair


def test_can_add_coin_transfer_block(
    memory_blockchain: MemoryBlockchain,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
    primary_validator_key_pair: KeyPair,
    node_key_pair: KeyPair,
    preferred_node,
):
    blockchain = memory_blockchain

    treasury_account = treasury_account_key_pair.public
    treasury_initial_balance = blockchain.get_account_current_balance(treasury_account)
    assert treasury_initial_balance is not None

    user_account = user_account_key_pair.public
    pv_account = primary_validator_key_pair.public
    node_account = node_key_pair.public

    total_fees = 1 + 4

    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=30,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
        preferred_node=preferred_node,
    )
    blockchain.add_block(block0)
    assert blockchain.get_account_current_balance(user_account) == 30
    assert blockchain.get_account_current_balance(node_account) == 1
    assert blockchain.get_account_current_balance(pv_account) == 4
    assert blockchain.get_account_current_balance(treasury_account) == treasury_initial_balance - 30 - total_fees

    with pytest.raises(ValidationError, match='Block number must be equal to next block number.*'):
        blockchain.add_block(block0)

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
        preferred_node=preferred_node,
    )
    blockchain.add_block(block1)
    assert blockchain.get_account_current_balance(user_account) == 40
    assert blockchain.get_account_current_balance(
        treasury_account
    ) == treasury_initial_balance - 30 - 10 - 2 * total_fees
    assert blockchain.get_account_current_balance(node_account) == 1 * 2
    assert blockchain.get_account_current_balance(pv_account) == 4 * 2

    block2 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=treasury_account,
        amount=5,
        request_signing_key=user_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
        preferred_node=preferred_node,
    )
    blockchain.add_block(block2)
    assert blockchain.get_account_current_balance(user_account) == 40 - 5 - total_fees
    assert blockchain.get_account_current_balance(
        treasury_account
    ) == treasury_initial_balance - 30 - 10 + 5 - 2 * total_fees
    assert blockchain.get_account_current_balance(node_account) == 1 * 3
    assert blockchain.get_account_current_balance(pv_account) == 4 * 3


def test_can_add_node_declaration_block(
    memory_blockchain: MemoryBlockchain,
    user_account_key_pair: KeyPair,
):
    blockchain = memory_blockchain
    user_account = user_account_key_pair.public

    request0 = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://127.0.0.1'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    block0 = Block.create_from_signed_change_request(blockchain, request0, get_node_signing_key())
    blockchain.add_block(block0)
    assert blockchain.get_node_by_identifier(user_account) == request0.message.node
    blockchain.snapshot_blockchain_state()
    assert blockchain.blockchain_states[-1].get_node(user_account) == request0.message.node

    request1 = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://127.0.0.2', 'http://192.168.0.34'],
        fee_amount=3,
        signing_key=user_account_key_pair.private
    )
    block1 = Block.create_from_signed_change_request(blockchain, request1, get_node_signing_key())
    blockchain.add_block(block1)
    assert blockchain.get_node_by_identifier(user_account) == request1.message.node
    blockchain.snapshot_blockchain_state()
    assert blockchain.blockchain_states[-1].get_node(user_account) == request1.message.node
