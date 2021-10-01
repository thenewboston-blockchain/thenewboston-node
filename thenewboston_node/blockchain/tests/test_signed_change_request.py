import copy
import json

import pytest
from rest_framework import status

from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.tests.base import (
    as_confirmation_validator, as_primary_validator, force_blockchain
)

API_V1_POST_SIGNED_CHANGE_REQUEST_URL = '/api/v1/signed-change-request/'


@pytest.mark.parametrize('interface', ('api_client', 'node_client'))
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_can_post_signed_change_request_to_pv(
    api_client, node_client, file_blockchain, user_account_key_pair, primary_validator_key_pair, interface
):
    blockchain = file_blockchain

    change_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node.non-existing-domain:8555/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private,
    )

    node = change_request.message.node
    node_identifier = node.identifier
    assert blockchain.get_node_role(identifier=node_identifier) is None

    with force_blockchain(blockchain), as_primary_validator():
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

        payload = change_request.serialize_to_dict()
        if interface == 'api_client':
            response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
            assert response.status_code == status.HTTP_201_CREATED
            response_json = response.json()
        else:
            response_json = node_client.send_signed_change_request_by_network_address(
                'http://testserver/', change_request
            )

        # TODO(dmu) LOW: Better deal with JSON normalization or serialization optimization
        payload['message']['node']['identifier'] = payload['signer']
        payload['message']['node']['fee_account'] = payload['message']['node'].get('fee_account')  # puts None
        assert response_json == payload

        response = api_client.get(f'/api/v1/nodes/{node_identifier}/')
        assert response.status_code == 200
        response_json = response.json()
        assert response_json == {
            'identifier': node_identifier,
            'role': 3,
            'network_addresses': ['http://new-node.non-existing-domain:8555/'],
            'fee_amount': 3,
            'fee_account': None,
        }

    assert blockchain.get_node_role(identifier=node_identifier) == NodeRole.REGULAR_NODE
    last_block_number = blockchain.get_last_block_number()
    assert blockchain.get_node_by_identifier(node_identifier, last_block_number) == node


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_signed_change_request_basic_validation(api_client, file_blockchain):
    blockchain = file_blockchain

    with force_blockchain(blockchain), as_primary_validator():
        payload = {}
        response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': ['Missing keys: message, signer']}


@pytest.mark.parametrize('interface', ('api_client', 'node_client'))
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_can_post_signed_change_request_to_cv(
    api_client, node_client, file_blockchain, user_account_key_pair, primary_validator_mock, interface
):
    blockchain = file_blockchain

    change_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node.non-existing-domain:8555/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private,
    )

    with force_blockchain(blockchain), as_confirmation_validator():
        response = api_client.get('/api/v1/nodes/self/')
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['role'] == NodeRole.CONFIRMATION_VALIDATOR.value

        payload = change_request.serialize_to_dict()
        if interface == 'api_client':
            response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
            assert response.status_code == status.HTTP_201_CREATED
            response_json = response.json()
        else:
            response_json = node_client.send_signed_change_request_by_network_address(
                'http://testserver/', change_request
            )

        # TODO(dmu) LOW: Better deal with JSON normalization or serialization optimization
        expected_response_json = copy.deepcopy(payload)
        expected_response_json['message']['node']['identifier'] = expected_response_json['signer']
        expected_response_json['message']['node']['fee_account'] = expected_response_json['message']['node'].get(
            'fee_account'
        )  # puts None
        assert response_json == expected_response_json

        latest_requests = primary_validator_mock.latest_requests()
        assert latest_requests
        latest_request = latest_requests[-1]
        assert latest_request.url == 'http://pv.non-existing-domain:8555/api/v1/signed-change-request/'
        body_json = json.loads(latest_request.body)
        assert body_json == payload
