import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.core.utils.cryptography import KeyPair


def test_get_account_balance_from_initial_account_root_file(
    forced_memory_blockchain: MemoryBlockchain, treasury_account_key_pair: KeyPair,
    initial_account_root_file: AccountRootFile
):
    account = treasury_account_key_pair.public
    assert forced_memory_blockchain.get_account_balance(account) == 281474976710656
    assert forced_memory_blockchain.get_account_balance(account
                                                        ) == initial_account_root_file.get_balance_value(account)


@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_get_account_balance_by_block_number(
    forced_memory_blockchain: MemoryBlockchain, treasury_account_key_pair: KeyPair, user_account_key_pair: KeyPair,
    primary_validator, preferred_node
):

    blockchain = forced_memory_blockchain
    sender = treasury_account_key_pair.public
    recipient = user_account_key_pair.public
    total_fees = primary_validator.fee_amount + preferred_node.fee_amount

    sender_initial_balance = blockchain.get_account_balance(sender)
    assert sender_initial_balance == 281474976710656
    assert blockchain.get_account_balance(sender, -1) == sender_initial_balance
    assert blockchain.get_account_balance(recipient) is None
    assert blockchain.get_account_balance(recipient, -1) is None

    block0 = Block.from_main_transaction(recipient, 10, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block0)
    assert blockchain.get_account_balance(sender) == sender_initial_balance - 10 - total_fees
    assert blockchain.get_account_balance(recipient) == 10

    block1 = Block.from_main_transaction(recipient, 11, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block1)
    assert blockchain.get_account_balance(sender) == sender_initial_balance - 10 - 11 - 2 * total_fees
    assert blockchain.get_account_balance(recipient) == 10 + 11

    block2 = Block.from_main_transaction(recipient, 12, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block2)
    assert blockchain.get_account_balance(sender) == sender_initial_balance - 10 - 11 - 12 - 3 * total_fees
    assert blockchain.get_account_balance(recipient) == 10 + 11 + 12

    assert blockchain.get_account_balance(sender, 2) == sender_initial_balance - 10 - 11 - 12 - 3 * total_fees
    assert blockchain.get_account_balance(recipient, 2) == 10 + 11 + 12
    assert blockchain.get_account_balance(sender, 1) == sender_initial_balance - 10 - 11 - 2 * total_fees
    assert blockchain.get_account_balance(recipient, 1) == 10 + 11
    assert blockchain.get_account_balance(sender, 0) == sender_initial_balance - 10 - total_fees
    assert blockchain.get_account_balance(recipient, 0) == 10
    assert blockchain.get_account_balance(sender, -1) == sender_initial_balance
    assert blockchain.get_account_balance(recipient, -1) is None
