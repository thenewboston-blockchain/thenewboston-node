import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.core.utils.cryptography import KeyPair


@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_add_block(
    forced_memory_blockchain: MemoryBlockchain,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
    primary_validator_key_pair: KeyPair,
    node_key_pair: KeyPair,
):
    blockchain = forced_memory_blockchain

    treasury_account = treasury_account_key_pair.public
    treasury_initial_balance = blockchain.get_balance_value(treasury_account)
    assert treasury_initial_balance is not None

    user_account = user_account_key_pair.public
    pv_account = primary_validator_key_pair.public
    node_account = node_key_pair.public

    total_fees = 1 + 4

    block0 = Block.from_main_transaction(blockchain, user_account, 30, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block0)
    assert blockchain.get_balance_value(user_account) == 30
    assert blockchain.get_balance_value(treasury_account) == treasury_initial_balance - 30 - total_fees
    assert blockchain.get_balance_value(node_account) == 1
    assert blockchain.get_balance_value(pv_account) == 4

    with pytest.raises(ValidationError, match='Block number must be equal to next block number.*'):
        blockchain.add_block(block0)

    block1 = Block.from_main_transaction(blockchain, user_account, 10, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block1)
    assert blockchain.get_balance_value(user_account) == 40
    assert blockchain.get_balance_value(treasury_account) == treasury_initial_balance - 30 - 10 - 2 * total_fees
    assert blockchain.get_balance_value(node_account) == 1 * 2
    assert blockchain.get_balance_value(pv_account) == 4 * 2

    block2 = Block.from_main_transaction(blockchain, treasury_account, 5, signing_key=user_account_key_pair.private)
    blockchain.add_block(block2)
    assert blockchain.get_balance_value(user_account) == 40 - 5 - total_fees
    assert blockchain.get_balance_value(treasury_account) == treasury_initial_balance - 30 - 10 + 5 - 2 * total_fees
    assert blockchain.get_balance_value(node_account) == 1 * 3
    assert blockchain.get_balance_value(pv_account) == 4 * 3
