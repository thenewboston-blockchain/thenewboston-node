import pytest

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode

primary_validator_fee = 5
node_fee = 3


@pytest.fixture(autouse=True)
def set_up(file_blockchain_w_memory_storage, user_account, signing_key, primary_validator_identifier, node_identifier):
    pv = PrimaryValidator(identifier=primary_validator_identifier, fee_amount=primary_validator_fee)
    node = RegularNode(identifier=node_identifier, fee_amount=node_fee)

    block = Block.from_main_transaction(file_blockchain_w_memory_storage, user_account, 100, signing_key, pv, node)
    file_blockchain_w_memory_storage.add_block(block)
    file_blockchain_w_memory_storage.make_account_root_file()


def test_last_block_data_is_correct(file_blockchain_w_memory_storage):
    account_root_file = file_blockchain_w_memory_storage.get_last_account_root_file()

    assert account_root_file.last_block_number == 0


def test_balances_are_correct(
    file_blockchain_w_memory_storage, treasury_account, user_account, primary_validator_identifier, node_identifier,
    treasury_initial_balance
):
    account_root_file = file_blockchain_w_memory_storage.get_last_account_root_file()
    accounts = account_root_file.accounts

    assert len(accounts) == 4
    assert accounts[treasury_account].value == treasury_initial_balance - primary_validator_fee - node_fee - 100
    assert accounts[user_account].value == 100
    assert accounts[primary_validator_identifier].value == primary_validator_fee
    assert accounts[node_identifier].value == node_fee
