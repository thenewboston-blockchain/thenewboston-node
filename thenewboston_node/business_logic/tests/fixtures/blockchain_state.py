import pytest

from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.business_logic.models.signed_change_request_message.pv_schedule import PrimaryValidatorSchedule


@pytest.fixture
def treasury_initial_balance():
    return 281474976710656


@pytest.fixture
def blockchain_genesis_state(treasury_account, treasury_initial_balance, primary_validator) -> BlockchainState:
    pv_identifier = primary_validator.identifier

    assert pv_identifier != treasury_account
    accounts = {
        treasury_account:
            AccountState(balance=treasury_initial_balance),
        pv_identifier:
            AccountState(
                node=primary_validator,
                primary_validator_schedule=PrimaryValidatorSchedule(begin_block_number=0, end_block_number=99)
            ),
    }
    return BlockchainState(account_states=accounts)


@pytest.fixture
def blockchain_genesis_state_dict(blockchain_genesis_state: BlockchainState) -> dict:
    return blockchain_genesis_state.to_dict()  # type: ignore


@pytest.fixture
def blockchain_state_10(treasury_initial_balance, treasury_account, user_account):
    user_balance = 1000
    return models.BlockchainState(
        last_block_number=10,
        account_states={
            treasury_account:
                AccountState(balance=treasury_initial_balance - user_balance, balance_lock=treasury_account),
            user_account:
                AccountState(balance=user_balance, balance_lock=user_account),
        },
    )


@pytest.fixture
def blockchain_state_20(treasury_initial_balance, treasury_account, user_account):
    user_balance = 2000
    return models.BlockchainState(
        last_block_number=20,
        account_states={
            treasury_account:
                AccountState(balance=treasury_initial_balance - user_balance, balance_lock=treasury_account),
            user_account:
                AccountState(balance=user_balance, balance_lock=user_account),
        },
    )
