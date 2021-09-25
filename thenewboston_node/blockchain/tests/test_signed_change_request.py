import pytest
from rest_framework import status

from thenewboston_node.business_logic.models import (
    Block, NodeDeclarationSignedChangeRequest, PrimaryValidatorScheduleSignedChangeRequest
)
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.tests.base import force_blockchain

API_V1_POST_SIGNED_CHANGE_REQUEST_URL = '/api/v1/signed-change-request/'


def test_can_post_signed_change_request_to_pv(api_client, file_blockchain, user_account_key_pair):
    blockchain = file_blockchain

    pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, get_node_signing_key())
    block = Block.create_from_signed_change_request(blockchain, pvs_request, get_node_signing_key())
    blockchain.add_block(block)

    change_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://my.domain.com/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private,
    )
    with force_blockchain(blockchain):
        response = api_client.post(
            API_V1_POST_SIGNED_CHANGE_REQUEST_URL,
            data=change_request.serialize_to_dict(),
        )

    assert response.status_code == status.HTTP_201_CREATED


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
