from django.test import override_settings

import pytest
from rest_framework import status

from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.tests.base import force_blockchain

API_V1_POST_SIGNED_CHANGE_REQUEST_URL = '/api/v1/signed-change-request/'


@pytest.mark.parametrize('interface', ('api_client', 'node_client'))
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_can_post_signed_change_request_to_pv(
    api_client, node_client, file_blockchain, user_account_key_pair, primary_validator_key_pair, interface
):
    blockchain = file_blockchain

    change_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://my.domain.com/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private,
    )

    with force_blockchain(blockchain):
        with override_settings(NODE_SIGNING_KEY=primary_validator_key_pair.private):
            response = api_client.get('/api/v1/nodes/self/')
            assert response.status_code == 200
            response_json = response.json()
            assert response_json['identifier'] == primary_validator_key_pair.public
            assert response_json['role'] == NodeRole.PRIMARY_VALIDATOR.value

            response = api_client.get('/api/v1/nodes/pv/')
            assert response.status_code == 200
            response_json = response.json()
            assert response_json['identifier'] == primary_validator_key_pair.public
            assert response_json['role'] == NodeRole.PRIMARY_VALIDATOR.value

            if interface == 'api_client':
                payload = change_request.serialize_to_dict()
                response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
                assert response.status_code == status.HTTP_201_CREATED
                response_json = response.json()
            else:
                response_json = node_client.post_signed_change_request_by_network_address(
                    'http://testserver/', change_request
                )

            # TODO(dmu) LOW: Better deal with JSON normalization or serialized optimization
            change_request_json = change_request.serialize_to_dict()
            change_request_json['message']['node']['identifier'] = change_request_json['signer']
            change_request_json['message']['node']['fee_account'] = change_request_json['message']['node'].get(
                'fee_account'
            )  # puts None if key does not exist
            assert response_json == change_request_json


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_can_post_signed_change_request_to_cv(api_client, file_blockchain, user_account_key_pair):
    blockchain = file_blockchain

    change_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://my.domain.com/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private,
    )
    with force_blockchain(blockchain):
        try:
            api_client.post(
                API_V1_POST_SIGNED_CHANGE_REQUEST_URL,
                data=change_request.serialize_to_dict(),
            )
        except RecursionError:
            pass
