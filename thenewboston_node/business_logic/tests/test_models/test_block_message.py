import copy

import pytest

from thenewboston_node.business_logic.exceptions import ValidationError


def test_validate_updated_account_states(memory_blockchain, block_message):
    assert block_message.updated_account_states
    assert len(block_message.updated_account_states) >= 2
    block_message.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states = None
    with pytest.raises(ValidationError, match='Block message updated_account_states must be not empty'):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states = dict([block_message_copy.updated_account_states.popitem()])
    with pytest.raises(ValidationError, match='Block message updated_account_states must contain at least 2 items'):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    signer = block_message_copy.signed_change_request.signer
    del block_message_copy.updated_account_states[signer]
    with pytest.raises(ValidationError, match=f'Block message updated_account_states.{signer} must be not empty'):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[None] = block_message_copy.updated_account_states[signer]
    with pytest.raises(
        ValidationError, match=r'Block message updated_account_states key \(account number\) must be not empty'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[''] = block_message_copy.updated_account_states[signer]
    with pytest.raises(
        ValidationError, match=r'Block message updated_account_states key \(account number\) must be not empty'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[1] = block_message_copy.updated_account_states[signer]
    with pytest.raises(
        ValidationError, match=r'Block message updated_account_states key \(account number\) must be string'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[signer].balance_lock = None
    with pytest.raises(
        ValidationError, match=f'Block message sender account {signer} '
        'balance_lock must be not empty'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[signer].balance_lock = ''
    with pytest.raises(ValidationError, match='Account state balance_lock must be not empty'):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[signer].balance_lock = 1
    with pytest.raises(ValidationError, match='Account state balance_lock must be string'):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[signer].balance_lock = 'fake'
    with pytest.raises(
        ValidationError, match=f'Block message sender account {signer} '
        'balance_lock must be equal to [0-9a-f]{64}'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    for key in list(block_message_copy.updated_account_states.keys()):
        if key == signer:
            continue

        block_message_copy.updated_account_states[key].balance_lock = 'v'

    with pytest.raises(
        ValidationError, match='Block message recipient account [0-9a-f]{64} balance_lock must be empty'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    block_message_copy.updated_account_states[signer].balance = 0
    with pytest.raises(
        ValidationError, match=f'Block message sender account {signer} '
        r'balance must be equal to \d+'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)

    block_message_copy = copy.deepcopy(block_message)
    for key in list(block_message_copy.updated_account_states.keys()):
        if key == signer:
            continue

        block_message_copy.updated_account_states[key].balance = 0

    with pytest.raises(
        ValidationError, match=r'Block message recipient account [0-9a-f]{64} balance must be equal to \d+'
    ):
        block_message_copy.validate_updated_account_states(memory_blockchain)
