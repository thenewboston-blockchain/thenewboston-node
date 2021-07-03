import pytest

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key


@pytest.fixture(autouse=True)
def set_up(file_blockchain_w_memory_storage, user_account, treasury_account_signing_key):
    signing_key = treasury_account_signing_key
    block = Block.create_from_main_transaction(
        blockchain=file_blockchain_w_memory_storage,
        recipient=user_account,
        amount=100,
        request_signing_key=signing_key,
        pv_signing_key=get_node_signing_key(),
    )
    file_blockchain_w_memory_storage.add_block(block)


def test_non_existent_account_balance_is_zero(file_blockchain_w_memory_storage):
    assert file_blockchain_w_memory_storage.get_account_current_balance('0' * 65) == 0


def test_can_get_account_state(file_blockchain_w_memory_storage, user_account):
    assert file_blockchain_w_memory_storage.get_account_current_balance(account=user_account) == 100


def test_validate_negative_before_block_number(file_blockchain_w_memory_storage, user_account):
    with pytest.raises(ValueError, match='block_number must be greater or equal to -1'):
        file_blockchain_w_memory_storage.get_account_balance(account=user_account, on_block_number=-2)

    with pytest.raises(ValueError, match='block_number must be greater or equal to -1'):
        file_blockchain_w_memory_storage.get_account_balance_lock(account=user_account, on_block_number=-2)


def test_validate_before_block_number_out_of_bound(file_blockchain_w_memory_storage, user_account):
    with pytest.raises(ValueError, match='block_number must be less than current block number'):
        file_blockchain_w_memory_storage.get_account_balance(account=user_account, on_block_number=999)

    with pytest.raises(ValueError, match='block_number must be less than current block number'):
        file_blockchain_w_memory_storage.get_account_balance_lock(account=user_account, on_block_number=999)


def test_get_account_state_before_transaction(file_blockchain_w_memory_storage, user_account):
    assert file_blockchain_w_memory_storage.get_account_balance(account=user_account, on_block_number=-1) == 0


def test_get_account_lock_before_transaction(file_blockchain_w_memory_storage, treasury_account):
    balance_lock = file_blockchain_w_memory_storage.get_account_balance_lock(
        account=treasury_account, on_block_number=-1
    )
    assert balance_lock == treasury_account


def test_account_lock_after_transaction(file_blockchain_w_memory_storage, treasury_account):
    block = file_blockchain_w_memory_storage.get_last_block()
    updated_treasury_balance = block.message.updated_account_states[treasury_account]

    balance_lock = file_blockchain_w_memory_storage.get_account_current_balance_lock(account=treasury_account)
    assert balance_lock == updated_treasury_balance.balance_lock
