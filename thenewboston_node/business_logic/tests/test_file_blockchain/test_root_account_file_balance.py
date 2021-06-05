import pytest

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode

primary_validator_fee = 5
node_fee = 3


@pytest.fixture(autouse=True)
def set_up(
    file_blockchain_w_memory_storage, user_account, treasury_account_signing_key, primary_validator_identifier,
    node_identifier
):
    signing_key = treasury_account_signing_key
    pv = PrimaryValidator(
        identifier=primary_validator_identifier, fee_amount=primary_validator_fee, network_addresses=[]
    )
    node = RegularNode(identifier=node_identifier, fee_amount=node_fee, network_addresses=[])

    block = Block.from_main_transaction(file_blockchain_w_memory_storage, user_account, 100, signing_key, pv, node)
    file_blockchain_w_memory_storage.add_block(block)
    file_blockchain_w_memory_storage.snapshot_blockchain_state()


def test_last_block_data_is_correct(file_blockchain_w_memory_storage):
    account_root_file = file_blockchain_w_memory_storage.get_last_blockchain_state()

    assert account_root_file.last_block_number == 0


def test_balances_are_correct(
    file_blockchain_w_memory_storage, treasury_account, user_account, primary_validator_identifier, node_identifier,
    treasury_initial_balance
):
    account_root_file = file_blockchain_w_memory_storage.get_last_blockchain_state()
    accounts = account_root_file.account_states

    assert len(accounts) == 4
    assert accounts[treasury_account].balance == treasury_initial_balance - primary_validator_fee - node_fee - 100
    assert accounts[user_account].balance == 100
    assert accounts[primary_validator_identifier].balance == primary_validator_fee
    assert accounts[node_identifier].balance == node_fee
