from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.tests.factories import add_blocks_to_blockchain


def test_can_get_account_balances(forced_memory_blockchain: MemoryBlockchain, api_client):
    blockchain = forced_memory_blockchain
    assert blockchain.account_root_files
    account_number = next(iter(blockchain.account_root_files[0].accounts.keys()))
    value = blockchain.get_balance_value(account_number)
    lock = blockchain.get_balance_lock(account_number)

    response = api_client.get(f'/api/v1/account-balances/{account_number}/')
    assert response.status_code == 200
    assert response.json() == {'balance': value, 'lock': lock}


def test_can_get_account_balances_on_file_blockchain(
    forced_file_blockchain: FileBlockchain, treasury_account_key_pair, api_client
):
    blockchain = forced_file_blockchain
    treasury_account_balance = blockchain.get_balance_value(treasury_account_key_pair.public)
    assert treasury_account_balance is not None
    assert treasury_account_balance > 100000000
    add_blocks_to_blockchain(blockchain, 5, treasury_account_key_pair.private)

    for account_number in blockchain.iter_known_accounts():
        value = blockchain.get_balance_value(account_number)
        lock = blockchain.get_balance_lock(account_number)

        response = api_client.get(f'/api/v1/account-balances/{account_number}/')
        assert response.status_code == 200
        assert response.json() == {'balance': value, 'lock': lock}
