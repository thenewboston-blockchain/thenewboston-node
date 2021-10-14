import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import (
    Block, NodeDeclarationSignedChangeRequest, PrimaryValidatorScheduleSignedChangeRequest
)


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_pv_from_blockchain_genesis_state(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    blockchain_state_nodes = list(blockchain.get_first_blockchain_state().yield_nodes())
    node = blockchain.get_primary_validator()

    assert blockchain.get_primary_validator() == node
    assert blockchain.get_primary_validator(0) == node
    assert blockchain.get_primary_validator(10) == node
    assert blockchain.get_primary_validator(99) == node
    assert blockchain.get_primary_validator(200) is None


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_pv_from_from_blocks(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, user_account_key_pair,
    blockchain_argument_name, primary_validator_key_pair
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    pv1 = blockchain.get_primary_validator()

    signing_key = user_account_key_pair.private
    nd_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node.non-existing.domain:8555/'], fee_amount=3, signing_key=signing_key
    )
    pv2 = nd_request.message.node
    assert pv2.identifier
    assert pv1 != pv2

    block = Block.create_from_signed_change_request(blockchain, nd_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(100, 199, signing_key)
    block = Block.create_from_signed_change_request(blockchain, pvs_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == pv1
    assert blockchain.get_primary_validator(10) == pv1
    assert blockchain.get_primary_validator(99) == pv1
    assert blockchain.get_primary_validator(100) == pv2
    assert blockchain.get_primary_validator(199) == pv2
    assert blockchain.get_primary_validator(200) is None


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_node_from_genesis_state_and_pv_from_blocks(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, primary_validator_key_pair,
    user_account_key_pair, blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    pv1 = blockchain.get_primary_validator()
    assert pv1 is not None
    assert primary_validator_key_pair.public == pv1.identifier

    pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 2, primary_validator_key_pair.private)
    block = Block.create_from_signed_change_request(blockchain, pvs_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == pv1
    assert blockchain.get_primary_validator(0) == pv1
    assert blockchain.get_primary_validator(1) == pv1
    assert blockchain.get_primary_validator(2) == pv1
    assert blockchain.get_primary_validator(3) is None

    signing_key = user_account_key_pair.private
    nd_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node.non-existing.domain:8555/'], fee_amount=3, signing_key=signing_key
    )
    pv2 = nd_request.message.node
    assert pv2.identifier
    assert pv1 != pv2

    block = Block.create_from_signed_change_request(blockchain, nd_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    blockchain.snapshot_blockchain_state()

    pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(3, 99, signing_key)
    block = Block.create_from_signed_change_request(blockchain, pvs_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    assert blockchain.get_next_block_number() == 3

    assert blockchain.get_primary_validator() == pv2
    assert blockchain.get_primary_validator(0) == pv1
    assert blockchain.get_primary_validator(1) == pv1
    assert blockchain.get_primary_validator(2) == pv1
    assert blockchain.get_primary_validator(3) == pv2
    assert blockchain.get_primary_validator(10) == pv2
    assert blockchain.get_primary_validator(99) == pv2
    assert blockchain.get_primary_validator(200) is None


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_overridden_pv(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, primary_validator_key_pair,
    user_account_key_pair, blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    blockchain_state_nodes = list(blockchain.get_first_blockchain_state().yield_nodes())
    pv1 = blockchain.get_primary_validator()
    assert pv1 is not None
    assert primary_validator_key_pair.public == pv1.identifier

    signing_key = user_account_key_pair.private
    nd_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node.non-existing.domain:8555/'], fee_amount=3, signing_key=signing_key
    )
    another_node = nd_request.message.node
    assert another_node.identifier
    assert pv1 != another_node

    block = Block.create_from_signed_change_request(blockchain, nd_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == pv1
    assert blockchain.get_primary_validator(0) == pv1
    assert blockchain.get_primary_validator(10) == pv1
    assert blockchain.get_primary_validator(99) == pv1
    assert blockchain.get_primary_validator(200) is None

    pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, signing_key)
    block = Block.create_from_signed_change_request(blockchain, pvs_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == another_node
    assert blockchain.get_primary_validator(0) == another_node
    assert blockchain.get_primary_validator(10) == another_node
    assert blockchain.get_primary_validator(99) == another_node
    assert blockchain.get_primary_validator(200) is None

    pvs_request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, primary_validator_key_pair.private)
    block = Block.create_from_signed_change_request(blockchain, pvs_request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == pv1
    assert blockchain.get_primary_validator(0) == pv1
    assert blockchain.get_primary_validator(10) == pv1
    assert blockchain.get_primary_validator(99) == pv1
    assert blockchain.get_primary_validator(200) is None
