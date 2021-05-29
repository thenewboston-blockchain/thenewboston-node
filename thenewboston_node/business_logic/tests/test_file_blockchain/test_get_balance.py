import pytest

from thenewboston_node.business_logic.models.block import Block


@pytest.fixture(autouse=True)
def set_up(file_blockchain_w_memory_storage, user_account, signing_key):
    block = Block.from_main_transaction(
        file_blockchain_w_memory_storage,
        recipient=user_account,
        amount=100,
        signing_key=signing_key,
    )
    file_blockchain_w_memory_storage.add_block(block)


def test_non_existent_account_balance_is_zero(file_blockchain_w_memory_storage):
    assert file_blockchain_w_memory_storage.get_account_balance('0' * 65) is None


def test_can_get_account_state(file_blockchain_w_memory_storage, user_account):
    assert file_blockchain_w_memory_storage.get_account_balance(account=user_account) == 100


def test_validate_negative_before_block_number(file_blockchain_w_memory_storage, user_account):
    with pytest.raises(ValueError, match='block_number must be greater or equal to 0'):
        file_blockchain_w_memory_storage.get_account_balance(account=user_account, before_block_number=-1)

    with pytest.raises(ValueError, match='block_number must be greater or equal to 0'):
        file_blockchain_w_memory_storage.get_account_lock(account=user_account, before_block_number=-1)


def test_validate_before_block_number_out_of_bound(file_blockchain_w_memory_storage, user_account):
    with pytest.raises(ValueError, match='block_number must be less or equal to next block number'):
        file_blockchain_w_memory_storage.get_account_balance(account=user_account, before_block_number=999)

    with pytest.raises(ValueError, match='block_number must be less or equal to next block number'):
        file_blockchain_w_memory_storage.get_account_lock(account=user_account, before_block_number=999)


def test_get_account_state_before_transaction(file_blockchain_w_memory_storage, user_account):
    assert file_blockchain_w_memory_storage.get_account_balance(account=user_account, before_block_number=0) is None


def test_get_account_lock_before_transaction(file_blockchain_w_memory_storage, treasury_account):
    balance_lock = file_blockchain_w_memory_storage.get_account_lock(account=treasury_account, before_block_number=0)
    assert balance_lock == treasury_account


def test_account_lock_after_transaction(file_blockchain_w_memory_storage, treasury_account):
    block = file_blockchain_w_memory_storage.get_last_block()
    updated_treasury_balance = block.message.updated_balances[treasury_account]

    balance_lock = file_blockchain_w_memory_storage.get_account_lock(account=treasury_account)
    assert balance_lock == updated_treasury_balance.lock
