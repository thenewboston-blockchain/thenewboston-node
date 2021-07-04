from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.tests.factories import add_blocks_to_blockchain


def test_can_get_account_states(forced_memory_blockchain: MemoryBlockchain, api_client):
    blockchain = forced_memory_blockchain
    assert blockchain.blockchain_states
    account_number = next(iter(blockchain.blockchain_states[0].account_states.keys()))
    balance = blockchain.get_account_current_balance(account_number)
    lock = blockchain.get_account_current_balance_lock(account_number)

    response = api_client.get(f'/api/v1/account-states/{account_number}/')
    assert response.status_code == 200
    assert response.json() == {
        'balance': balance,
        'balance_lock': lock,
        'node': None,
        'primary_validator_schedule': None
    }


def test_can_get_account_states_on_file_blockchain(
    forced_file_blockchain: FileBlockchain, treasury_account_key_pair, api_client
):
    blockchain = forced_file_blockchain
    treasury_account_balance = blockchain.get_account_current_balance(treasury_account_key_pair.public)
    assert treasury_account_balance is not None
    assert treasury_account_balance > 100000000
    add_blocks_to_blockchain(blockchain, 5, treasury_account_key_pair.private)

    for account_number in blockchain.yield_known_accounts():
        balance = blockchain.get_account_current_balance(account_number)
        lock = blockchain.get_account_current_balance_lock(account_number)

        response = api_client.get(f'/api/v1/account-states/{account_number}/')
        assert response.status_code == 200
        assert response.json() == {
            'balance': balance,
            'balance_lock': lock,
            'node': None,
            'primary_validator_schedule': None
        }


def test_yield_known_accounts(forced_file_blockchain: FileBlockchain, treasury_account_key_pair):
    blockchain = forced_file_blockchain
    treasury_account_balance = blockchain.get_account_current_balance(treasury_account_key_pair.public)
    assert treasury_account_balance is not None
    assert treasury_account_balance > 100000000
    add_blocks_to_blockchain(blockchain, 5, treasury_account_key_pair.private)
    known_accounts = set(blockchain.get_first_blockchain_state().account_states.keys())
    for block in blockchain.yield_blocks():
        known_accounts.update(account for account, _ in block.yield_account_states())

    assert set(blockchain.yield_known_accounts()) == known_accounts
