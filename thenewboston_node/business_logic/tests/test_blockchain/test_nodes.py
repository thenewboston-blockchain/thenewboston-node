import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest
from thenewboston_node.core.utils.cryptography import generate_key_pair


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_single_node_from_blockchain_genesis_state(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]
    assert list(blockchain.yield_nodes()) == list(blockchain.get_first_blockchain_state().yield_nodes())


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_from_genesis_state_and_blocks(
    file_blockchain: BlockchainBase,
    memory_blockchain: BlockchainBase,
    user_account_key_pair,
    blockchain_argument_name,
    primary_validator_key_pair,
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node.non-existing.domain:8555/'],
        fee_amount=3,
        signing_key=user_account_key_pair.private
    )
    blocks_node = request.message.node
    assert blocks_node.identifier

    block = Block.create_from_signed_change_request(blockchain, request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    blockchain_state_nodes = list(blockchain.get_first_blockchain_state().yield_nodes())
    assert list(blockchain.yield_nodes()) == [blocks_node] + blockchain_state_nodes


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_blocks_node_overrides_genesis_state_node(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, primary_validator_key_pair,
    blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    initial_nodes = set(blockchain.yield_nodes())
    initial_pv_node = blockchain.get_primary_validator()
    assert initial_pv_node is not None
    initial_nodes_except_pv = initial_nodes - {initial_pv_node}
    assert primary_validator_key_pair.public == initial_pv_node.identifier

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node.non-existing.domain:8555/'],
        fee_amount=3,
        signing_key=primary_validator_key_pair.private
    )
    blocks_node = request.message.node
    assert blocks_node.identifier
    assert blocks_node.identifier == initial_pv_node.identifier

    block = Block.create_from_signed_change_request(blockchain, request, primary_validator_key_pair.private)
    blockchain.add_block(block)

    assert blocks_node != initial_pv_node
    assert set(blockchain.yield_nodes()) == {blocks_node} | initial_nodes_except_pv


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_from_different_block_numbers(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, primary_validator_key_pair,
    blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    initial_nodes = set(blockchain.yield_nodes())
    initial_pv_node = blockchain.get_primary_validator()
    assert initial_pv_node is not None
    initial_nodes_except_pv = initial_nodes - {initial_pv_node}
    assert primary_validator_key_pair.public == initial_pv_node.identifier
    signing_key = primary_validator_key_pair.private

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node1.non-existing-domain:8555/'], fee_amount=3, signing_key=signing_key
    )
    node0 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node2.non-existing-domain:8555/'], fee_amount=3, signing_key=signing_key
    )
    node1 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node3.non-existing-domain:8555/'], fee_amount=3, signing_key=signing_key
    )
    node2 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    assert set(blockchain.yield_nodes()) == {node2} | initial_nodes_except_pv
    assert set(blockchain.yield_nodes(block_number=2)) == {node2} | initial_nodes_except_pv
    assert set(blockchain.yield_nodes(block_number=1)) == {node1} | initial_nodes_except_pv
    assert set(blockchain.yield_nodes(block_number=0)) == {node0} | initial_nodes_except_pv
    assert set(blockchain.yield_nodes(block_number=-1)) == initial_nodes


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_from_complex_blockchain(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, blockchain_argument_name,
    primary_validator_key_pair
):
    key_pair1 = generate_key_pair()
    key_pair2 = generate_key_pair()
    key_pair3 = generate_key_pair()
    key_pair4 = generate_key_pair()
    key_pair5 = generate_key_pair()
    assert len({key_pair1.public, key_pair2.public, key_pair3.public, key_pair4.public, key_pair5.public}) == 5

    blockchain: BlockchainBase = locals()[blockchain_argument_name]
    initial_nodes = set(blockchain.get_first_blockchain_state().yield_nodes())

    signing_key = primary_validator_key_pair.private
    # Block 0
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node1.non-existing-domain:8555/'], fee_amount=3, signing_key=key_pair1.private
    )
    node1 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    # Block 1
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://old-node2.non-existing-domain:8555/'], fee_amount=3, signing_key=key_pair2.private
    )
    node2_old = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    # Block 2
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node3.non-existing-domain:8555/'], fee_amount=3, signing_key=key_pair3.private
    )
    node3 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    assert set(blockchain.yield_nodes(block_number=2)) == {node3, node2_old, node1} | initial_nodes

    blockchain.snapshot_blockchain_state()

    # Block 3
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node2.non-existing-domain:8555/'], fee_amount=3, signing_key=key_pair2.private
    )
    node2 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    # Block 4
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node4.non-existing-domain:8555/'], fee_amount=3, signing_key=key_pair4.private
    )
    node4 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    # Block 5
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://new-node5.non-existing-domain:8555/'], fee_amount=3, signing_key=key_pair5.private
    )
    node5 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, signing_key))

    assert set(blockchain.yield_nodes()) == {node5, node4, node2, node3, node1} | initial_nodes
    assert set(blockchain.yield_nodes(block_number=5)) == {node5, node4, node2, node3, node1} | initial_nodes
    assert set(blockchain.yield_nodes(block_number=4)) == {node4, node2, node3, node1} | initial_nodes
    assert set(blockchain.yield_nodes(block_number=3)) == {node2, node3, node1} | initial_nodes
    assert set(blockchain.yield_nodes(block_number=2)) == {node3, node2_old, node1} | initial_nodes
    assert set(blockchain.yield_nodes(block_number=1)) == {node2_old, node1} | initial_nodes
    assert set(blockchain.yield_nodes(block_number=0)) == {node1} | initial_nodes
    assert set(blockchain.yield_nodes(block_number=-1)) == initial_nodes
