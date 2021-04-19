from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain


def test_can_get_account_balances(forced_memory_blockchain: MemoryBlockchain, api_client):
    assert forced_memory_blockchain.account_root_files
    account_number = next(iter(forced_memory_blockchain.account_root_files[0].accounts.keys()))
    value = forced_memory_blockchain.get_balance_value(account_number)
    lock = forced_memory_blockchain.get_balance_lock(account_number)

    response = api_client.get(f'/api/v1/account-balances/{account_number}/')
    assert response.status_code == 200
    assert response.json() == {'value': value, 'lock': lock}
