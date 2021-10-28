import json

import pytest
from rest_framework import status

from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest
from thenewboston_node.business_logic.tests.base import (
    as_confirmation_validator, as_primary_validator, force_blockchain
)

from .base import API_V1_POST_SIGNED_CHANGE_REQUEST_URL


@pytest.mark.parametrize('interface', ('api_client', 'node_client'))
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_can_post_coin_transfer_scr_to_pv(
    api_client, node_client, file_blockchain, user_account_key_pair, primary_validator_key_pair, preferred_node,
    interface
):
    blockchain = file_blockchain
    recipient = user_account_key_pair.public

    last_block_number = blockchain.get_last_block_number()
    expected_identifier = blockchain.get_next_block_identifier()
    assert blockchain.get_account_current_balance(recipient) == 0

    change_request = CoinTransferSignedChangeRequest.create_from_main_transaction(
        blockchain=blockchain,
        recipient=recipient,
        amount=3,
        signing_key=blockchain._test_treasury_account_key_pair.private,
        node=preferred_node,
    )

    with force_blockchain(blockchain), as_primary_validator():
        # TODO(dmu) CRITICAL: Assert / memorize for the amount on user_account_key_pair.public

        payload = change_request.serialize_to_dict()
        if interface == 'api_client':
            response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
            assert response.status_code == status.HTTP_201_CREATED
            response.json()
        else:
            node_client.send_signed_change_request_by_network_address('http://testserver/', change_request)

    assert blockchain.get_last_block_number() == last_block_number + 1
    assert blockchain.get_account_current_balance(recipient) == 3
    last_block = blockchain.get_last_block()
    assert last_block.message.block_type == 'ct'
    assert last_block.message.block_identifier == expected_identifier
    assert last_block.message.signed_change_request.signer == blockchain._test_treasury_account_key_pair.public


@pytest.mark.parametrize('interface', ('api_client', 'node_client'))
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_can_post_coin_transfer_scr_to_cv(
    api_client, node_client, file_blockchain, user_account_key_pair, preferred_node, primary_validator_mock, interface
):
    blockchain = file_blockchain
    recipient = user_account_key_pair.public

    change_request = CoinTransferSignedChangeRequest.create_from_main_transaction(
        blockchain=blockchain,
        recipient=recipient,
        amount=3,
        signing_key=blockchain._test_treasury_account_key_pair.private,
        node=preferred_node,
    )

    with force_blockchain(blockchain), as_confirmation_validator():
        payload = change_request.serialize_to_dict()
        if interface == 'api_client':
            response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
            assert response.status_code == status.HTTP_201_CREATED
            response.json()
        else:
            node_client.send_signed_change_request_by_network_address('http://testserver/', change_request)

        latest_requests = primary_validator_mock.latest_requests()
        assert latest_requests
        latest_request = latest_requests[-1]
        assert latest_request.url == 'http://pv.non-existing-domain:8555/api/v1/signed-change-request/'
        body_json = json.loads(latest_request.body)
        assert body_json == payload
