from django.test import override_settings

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models import (
    Block, NodeDeclarationSignedChangeRequest, PrimaryValidatorScheduleSignedChangeRequest
)
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.cryptography import derive_public_key

API_V1_NODES_PREFIX = '/api/v1/nodes'


def test_node_not_found(forced_memory_blockchain: MemoryBlockchain, api_client):
    node_id = 'non_existing_id'

    response = api_client.get(f'{API_V1_NODES_PREFIX}/{node_id}/')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Node not found'


def test_can_get_node(forced_memory_blockchain, api_client, user_account_key_pair):
    blockchain = forced_memory_blockchain
    node_declaration_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://my.domain.com/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private,
    )
    block = Block.create_from_signed_change_request(
        blockchain,
        signed_change_request=node_declaration_request,
        pv_signing_key=user_account_key_pair.private,
    )
    blockchain.add_block(block)

    node = node_declaration_request.message.node
    response = api_client.get(f'{API_V1_NODES_PREFIX}/{node.identifier}/')

    assert response.status_code == 200
    data = response.json()
    assert data['identifier'] == node.identifier
    assert data['fee_amount'] == 3


@override_settings(SIGNING_KEY='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732')
def test_can_get_self_node(forced_memory_blockchain, api_client):
    blockchain = forced_memory_blockchain
    signing_key = get_node_signing_key()
    node_id = derive_public_key(signing_key)
    node_declaration_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://my.domain.com/'],
        fee_amount=3,
        signing_key=signing_key,
    )
    block = Block.create_from_signed_change_request(
        blockchain,
        signed_change_request=node_declaration_request,
        pv_signing_key=signing_key,
    )
    blockchain.add_block(block)

    response = api_client.get(f'{API_V1_NODES_PREFIX}/self/')

    assert response.status_code == 200
    data = response.json()
    assert data['identifier'] == node_id
    assert data['fee_amount'] == 3


def test_can_get_primary_validator_node(forced_memory_blockchain, api_client):
    blockchain = forced_memory_blockchain
    signing_key = get_node_signing_key()

    pv_node_declaration_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://my.domain.com/'],
        fee_amount=3,
        signing_key=signing_key,
    )
    block = Block.create_from_signed_change_request(
        blockchain,
        signed_change_request=pv_node_declaration_request,
        pv_signing_key=signing_key,
    )
    blockchain.add_block(block)
    pv_node = pv_node_declaration_request.message.node

    pv_schedule_request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, signing_key=signing_key)
    block = Block.create_from_signed_change_request(
        blockchain,
        signed_change_request=pv_schedule_request,
        pv_signing_key=signing_key,
    )
    blockchain.add_block(block)

    response = api_client.get(f'{API_V1_NODES_PREFIX}/pv/')

    assert response.status_code == 200
    data = response.json()
    assert data['identifier'] == pv_node.identifier
    assert data['fee_amount'] == 3
