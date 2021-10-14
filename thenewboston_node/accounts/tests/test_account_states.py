from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.tests.base import as_primary_validator, force_blockchain
from thenewboston_node.business_logic.tests.factories import add_blocks


def test_can_get_account_states(file_blockchain: FileBlockchain, treasury_account_key_pair, api_client):
    blockchain = file_blockchain

    treasury_account_balance = blockchain.get_account_current_balance(treasury_account_key_pair.public)
    nodes = list(blockchain.yield_nodes())
    assert len(nodes) == 3
    node_identifiers = {node.identifier for node in nodes}

    assert treasury_account_balance is not None
    assert treasury_account_balance > 100000000
    add_blocks(
        blockchain,
        5,
        treasury_account_key_pair.private,
        signing_key=blockchain._test_primary_validator_key_pair.private  # type: ignore
    )

    with force_blockchain(blockchain), as_primary_validator():
        for account_number in blockchain.yield_known_accounts():
            balance = blockchain.get_account_current_balance(account_number)
            lock = blockchain.get_account_current_balance_lock(account_number)

            response = api_client.get(f'/api/v1/account-states/{account_number}/')
            assert response.status_code == 200
            response_json = response.json()
            assert response_json['balance'] == balance
            assert response_json['balance_lock'] == lock

            if account_number in node_identifiers:
                account_state = blockchain.get_account_state(account_number)
                node = account_state.node
                assert node
                node_json = response_json['node']
                assert node_json
                assert node_json['network_addresses'] == node.network_addresses
                assert node_json['fee_amount'] == node.fee_amount
                assert node_json['identifier'] == node.identifier
                assert node_json['fee_account'] is None

                pv_schedule = account_state.primary_validator_schedule
                if pv_schedule:
                    pv_schedule_json = response_json['primary_validator_schedule']
                    assert pv_schedule_json['begin_block_number'] == pv_schedule.begin_block_number
                    assert pv_schedule_json['end_block_number'] == pv_schedule.end_block_number
            else:
                assert 'node' in response_json
                assert 'primary_validator_schedule' in response_json


def test_yield_known_accounts(file_blockchain: FileBlockchain, treasury_account_key_pair):
    blockchain = file_blockchain
    treasury_account_balance = blockchain.get_account_current_balance(treasury_account_key_pair.public)
    assert treasury_account_balance is not None
    assert treasury_account_balance > 100000000
    add_blocks(
        blockchain,
        5,
        treasury_account_key_pair.private,
        signing_key=blockchain._test_primary_validator_key_pair.private  # type: ignore
    )
    known_accounts = set(blockchain.get_first_blockchain_state().account_states.keys())
    for block in blockchain.yield_blocks():
        known_accounts.update(account for account, _ in block.yield_account_states())

    assert set(blockchain.yield_known_accounts()) == known_accounts
