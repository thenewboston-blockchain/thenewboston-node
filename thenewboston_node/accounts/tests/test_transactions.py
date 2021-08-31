import random
from urllib.parse import urlencode

from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.tests.base import force_blockchain

API_V1_LIST_TRANSACTIONS_URL_PATTERN = '/api/v1/accounts/{id}/transactions/'


def test_can_list_transactions(
    api_client, file_blockchain, treasury_account_key_pair, user_account_key_pair, primary_validator_key_pair,
    preferred_node, preferred_node_key_pair
):
    blockchain = file_blockchain
    user_account_number = user_account_key_pair.public
    pv_signing_key = get_node_signing_key()

    recieve_transactions_count = random.randint(1, 3)
    send_transactions_count = random.randint(1, 3)
    total_transactions_count = recieve_transactions_count + send_transactions_count * 3

    for _ in range(recieve_transactions_count):
        block = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account_number,
            amount=100,
            request_signing_key=treasury_account_key_pair.private,
            pv_signing_key=pv_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block)

    for _ in range(send_transactions_count):
        block = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=primary_validator_key_pair.public,
            amount=5,
            request_signing_key=user_account_key_pair.private,
            pv_signing_key=pv_signing_key,
            preferred_node=preferred_node,
        )
        blockchain.add_block(block)

    with force_blockchain(blockchain):
        params = urlencode({'limit': total_transactions_count * 2})
        response = api_client.get(API_V1_LIST_TRANSACTIONS_URL_PATTERN.format(id=user_account_number) + '?' + params)

    assert response.status_code == 200
    data = response.json()

    results = data['results']
    assert len(results) == total_transactions_count

    for n in range(recieve_transactions_count):
        assert results[n].items() >= {
            'recipient': user_account_number,
            'amount': 100,
            'is_fee': False,
        }.items()

    for n in range(recieve_transactions_count, recieve_transactions_count + send_transactions_count, 3):
        assert results[n].items() >= {
            'recipient': primary_validator_key_pair.public,
            'amount': 5,
            'is_fee': False,
        }.items()
        assert results[n + 1].items() >= {
            'recipient': primary_validator_key_pair.public,
            'amount': 4,
            'is_fee': True,
        }.items()
        assert results[n + 2].items() >= {
            'recipient': preferred_node_key_pair.public,
            'amount': 1,
            'is_fee': True,
        }.items()
