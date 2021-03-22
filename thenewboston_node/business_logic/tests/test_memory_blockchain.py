import copy

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.tests.factories.block import make_block, make_block_message
from thenewboston_node.core.utils.cryptography import KeyPair


@pytest.mark.usefixtures('forced_memory_blockchain')
def test_can_forced_memory_blockchain():
    assert isinstance(BlockchainBase.get_instance(), MemoryBlockchain)


def test_get_account_balance_from_initial_account_root_file(
    forced_memory_blockchain: MemoryBlockchain, treasury_account_key_pair: KeyPair,
    initial_account_root_file: AccountRootFile
):
    account = treasury_account_key_pair.public
    assert forced_memory_blockchain.get_account_balance(account) == 281474976710656
    assert forced_memory_blockchain.get_account_balance(account
                                                        ) == initial_account_root_file.get_balance_value(account)


def test_get_latest_account_root_file(forced_memory_blockchain: MemoryBlockchain, initial_account_root_file):
    account_root_files = forced_memory_blockchain.account_root_files
    assert len(account_root_files) == 1
    assert forced_memory_blockchain.get_latest_account_root_file() == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(-1) == initial_account_root_file

    account_root_file1 = copy.deepcopy(initial_account_root_file)
    account_root_file1.last_block_number = 3
    forced_memory_blockchain.account_root_files.append(account_root_file1)

    assert len(account_root_files) == 2
    assert forced_memory_blockchain.get_latest_account_root_file() == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(-1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(0) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(2) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(3) == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(4) == account_root_file1

    account_root_file2 = copy.deepcopy(initial_account_root_file)
    account_root_file2.last_block_number = 5
    forced_memory_blockchain.account_root_files.append(account_root_file2)

    assert len(account_root_files) == 3
    assert forced_memory_blockchain.get_latest_account_root_file() == account_root_file2
    assert forced_memory_blockchain.get_latest_account_root_file(-1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(0) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(2) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(3) == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(4) == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(5) == account_root_file2
    assert forced_memory_blockchain.get_latest_account_root_file(6) == account_root_file2


def test_get_blocks_until_account_root_file(forced_memory_blockchain: MemoryBlockchain, initial_account_root_file):

    forced_memory_blockchain.blocks = [
        make_block(message=make_block_message(block_number=x, block_identifier=str(x))) for x in range(9)
    ]
    account_root_files = forced_memory_blockchain.account_root_files
    assert len(account_root_files) == 1
    assert forced_memory_blockchain.get_latest_account_root_file() == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(-1) == initial_account_root_file
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file()
            ] == [8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(5)
            ] == [5, 4, 3, 2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(1)
            ] == [1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(0)
            ] == [0]

    account_root_file1 = copy.deepcopy(initial_account_root_file)
    account_root_file1.last_block_number = 3
    forced_memory_blockchain.account_root_files.append(account_root_file1)

    assert len(account_root_files) == 2
    assert forced_memory_blockchain.get_latest_account_root_file() == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(-1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(0) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(2) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(3) == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(4) == account_root_file1

    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file()
            ] == [8, 7, 6, 5, 4]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(5)
            ] == [5, 4]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(3)
            ] == []
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(2)
            ] == [2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(1)
            ] == [1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(0)
            ] == [0]

    account_root_file2 = copy.deepcopy(initial_account_root_file)
    account_root_file2.last_block_number = 5
    forced_memory_blockchain.account_root_files.append(account_root_file2)

    assert len(account_root_files) == 3
    assert forced_memory_blockchain.get_latest_account_root_file() == account_root_file2
    assert forced_memory_blockchain.get_latest_account_root_file(-1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(0) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(1) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(2) == initial_account_root_file
    assert forced_memory_blockchain.get_latest_account_root_file(3) == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(4) == account_root_file1
    assert forced_memory_blockchain.get_latest_account_root_file(5) == account_root_file2
    assert forced_memory_blockchain.get_latest_account_root_file(6) == account_root_file2

    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file()
            ] == [8, 7, 6]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(8)
            ] == [8, 7, 6]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(7)
            ] == [7, 6]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(6)
            ] == [6]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(5)
            ] == []
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(4)
            ] == [4]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(3)
            ] == []
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(2)
            ] == [2, 1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(1)
            ] == [1, 0]
    assert [block.message.block_number for block in forced_memory_blockchain.get_blocks_until_account_root_file(0)
            ] == [0]


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
    treasury_initial_balance = blockchain.get_account_balance(treasury_account)
    assert treasury_initial_balance is not None

    user_account = user_account_key_pair.public
    pv_account = primary_validator_key_pair.public
    node_account = node_key_pair.public

    total_fees = 1 + 4

    block0 = Block.from_main_transaction(user_account, 30, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block0)
    assert blockchain.get_account_balance(user_account) == 30
    assert blockchain.get_account_balance(treasury_account) == treasury_initial_balance - 30 - total_fees
    assert blockchain.get_account_balance(node_account) == 1
    assert blockchain.get_account_balance(pv_account) == 4

    with pytest.raises(ValidationError, match='Balance key does not match balance lock'):
        blockchain.add_block(block0)

    block1 = Block.from_main_transaction(user_account, 10, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block1)
    assert blockchain.get_account_balance(user_account) == 40
    assert blockchain.get_account_balance(treasury_account) == treasury_initial_balance - 30 - 10 - 2 * total_fees
    assert blockchain.get_account_balance(node_account) == 1 * 2
    assert blockchain.get_account_balance(pv_account) == 4 * 2

    block2 = Block.from_main_transaction(treasury_account, 5, signing_key=user_account_key_pair.private)
    blockchain.add_block(block2)
    assert blockchain.get_account_balance(user_account) == 30
    assert blockchain.get_account_balance(treasury_account) == treasury_initial_balance - 30 - 10 + 5 - 2 * total_fees
    assert blockchain.get_account_balance(node_account) == 1 * 3
    assert blockchain.get_account_balance(pv_account) == 4 * 3
