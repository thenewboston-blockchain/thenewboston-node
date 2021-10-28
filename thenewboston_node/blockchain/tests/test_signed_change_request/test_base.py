import pytest
from rest_framework import status

from thenewboston_node.business_logic.tests.base import as_primary_validator, force_blockchain

from .base import API_V1_POST_SIGNED_CHANGE_REQUEST_URL


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_signed_change_request_basic_validation(api_client, file_blockchain):
    blockchain = file_blockchain

    with force_blockchain(blockchain), as_primary_validator():
        payload = {}
        response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'message': ['This field is required.']}

    with force_blockchain(blockchain), as_primary_validator():
        payload = {'message': {'signed_change_request_type': 'nd'}}
        response = api_client.post(API_V1_POST_SIGNED_CHANGE_REQUEST_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': ['Missing keys: signer']}
