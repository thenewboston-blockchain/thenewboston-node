import pytest

from thenewboston_node.business_logic.models.block import Block


def add_block(blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair):
    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=100,
        request_signing_key=treasury_account_signing_key,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    blockchain.add_block(block)


def test_non_existent_account_balance_is_zero(file_blockchain):
    assert file_blockchain.get_account_current_balance('0' * 65) == 0


def test_can_get_account_state(
    file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair
):
    add_block(file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair)
    assert file_blockchain.get_account_current_balance(account=user_account) == 100


def test_validate_negative_before_block_number(
    file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair
):
    add_block(file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair)

    with pytest.raises(ValueError, match='block_number must be greater or equal to -1'):
        file_blockchain.get_account_balance(account=user_account, on_block_number=-2)

    with pytest.raises(ValueError, match='block_number must be greater or equal to -1'):
        file_blockchain.get_account_balance_lock(account=user_account, on_block_number=-2)


def test_validate_before_block_number_out_of_bound(
    file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair
):
    add_block(file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair)

    with pytest.raises(ValueError, match='block_number must be less than current block number'):
        file_blockchain.get_account_balance(account=user_account, on_block_number=999)

    with pytest.raises(ValueError, match='block_number must be less than current block number'):
        file_blockchain.get_account_balance_lock(account=user_account, on_block_number=999)


def test_get_account_state_before_transaction(
    file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair
):
    add_block(file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair)
    assert file_blockchain.get_account_balance(account=user_account, on_block_number=-1) == 0


def test_get_account_lock_before_transaction(
    file_blockchain, user_account, treasury_account, treasury_account_signing_key, preferred_node,
    primary_validator_key_pair
):
    add_block(file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair)
    balance_lock = file_blockchain.get_account_balance_lock(account=treasury_account, on_block_number=-1)
    assert balance_lock == treasury_account


def test_account_lock_after_transaction(
    file_blockchain, user_account, treasury_account, treasury_account_signing_key, preferred_node,
    primary_validator_key_pair
):
    add_block(file_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator_key_pair)
    block = file_blockchain.get_last_block()
    updated_treasury_balance = block.message.updated_account_states[treasury_account]

    balance_lock = file_blockchain.get_account_current_balance_lock(account=treasury_account)
    assert balance_lock == updated_treasury_balance.balance_lock
