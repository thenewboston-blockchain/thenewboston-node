import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.cryptography import generate_key_pair


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_single_node_from_blockchain_genesis_state(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]
    assert list(blockchain.yield_nodes()) == list(blockchain.get_first_blockchain_state().yield_nodes())


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_from_genesis_state_and_blocks(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, user_account_key_pair, blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://127.0.0.1:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    blocks_node = request.message.node
    assert blocks_node.identifier

    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())
    blockchain.add_block(block)

    blockchain_state_nodes = list(blockchain.get_first_blockchain_state().yield_nodes())
    assert list(blockchain.yield_nodes()) == [blocks_node] + blockchain_state_nodes


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_blocks_node_overrides_genesis_state_node(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, primary_validator_key_pair,
    blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]

    blockchain_state_nodes = list(blockchain.get_first_blockchain_state().yield_nodes())
    assert len(blockchain_state_nodes) == 1
    blockchain_state_node = blockchain_state_nodes[0]
    assert primary_validator_key_pair.public == blockchain_state_node.identifier

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://127.0.0.1:8555/'], fee_amount=3, signing_key=primary_validator_key_pair.private
    )
    blocks_node = request.message.node
    assert blocks_node.identifier
    assert blocks_node.identifier == blockchain_state_node.identifier

    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())
    blockchain.add_block(block)

    assert blocks_node != blockchain_state_node
    assert list(blockchain.yield_nodes()) == [blocks_node]


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_from_different_block_numbers(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, primary_validator_key_pair,
    blockchain_argument_name
):
    blockchain: BlockchainBase = locals()[blockchain_argument_name]
    blockchain_state_nodes = list(blockchain.get_first_blockchain_state().yield_nodes())
    assert len(blockchain_state_nodes) == 1
    blockchain_state_node = blockchain_state_nodes[0]
    assert primary_validator_key_pair.public == blockchain_state_node.identifier
    signing_key = primary_validator_key_pair.private

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.30:8555/'], fee_amount=3, signing_key=signing_key
    )
    node0 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.31:8555/'], fee_amount=3, signing_key=signing_key
    )
    node1 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.32:8555/'], fee_amount=3, signing_key=signing_key
    )
    node2 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    assert list(blockchain.yield_nodes()) == [node2]
    assert list(blockchain.yield_nodes(block_number=2)) == [node2]
    assert list(blockchain.yield_nodes(block_number=1)) == [node1]
    assert list(blockchain.yield_nodes(block_number=0)) == [node0]
    assert list(blockchain.yield_nodes(block_number=-1)) == [blockchain_state_node]


@pytest.mark.parametrize('blockchain_argument_name', ('memory_blockchain', 'file_blockchain'))
def test_can_get_nodes_from_complex_blockchain(
    file_blockchain: BlockchainBase, memory_blockchain: BlockchainBase, blockchain_argument_name
):
    key_pair1 = generate_key_pair()
    key_pair2 = generate_key_pair()
    key_pair3 = generate_key_pair()
    key_pair4 = generate_key_pair()
    key_pair5 = generate_key_pair()
    key_pair6 = generate_key_pair()
    assert len({
        key_pair1.public, key_pair2.public, key_pair3.public, key_pair4.public, key_pair5.public, key_pair6.public
    }) == 6

    blockchain: BlockchainBase = locals()[blockchain_argument_name]
    blockchain_state_nodes = list(blockchain.get_first_blockchain_state().yield_nodes())
    assert len(blockchain_state_nodes) == 1
    node1 = blockchain_state_nodes[0]

    # Block 0
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.30:8555/'], fee_amount=3, signing_key=key_pair2.private
    )
    node2 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    # Block 1
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.31:8555/'], fee_amount=3, signing_key=key_pair3.private
    )
    node3_old = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    # Block 2
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.32:8555/'], fee_amount=3, signing_key=key_pair4.private
    )
    node4 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    assert set(blockchain.yield_nodes(block_number=2)) == {node4, node3_old, node2, node1}

    blockchain.snapshot_blockchain_state()

    # Block 3
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.33:8555/'], fee_amount=3, signing_key=key_pair3.private
    )
    node3 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    # Block 4
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.34:8555/'], fee_amount=3, signing_key=key_pair5.private
    )
    node5 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    # Block 5
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.35:8555/'], fee_amount=3, signing_key=key_pair6.private
    )
    node6 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request, get_node_signing_key()))

    assert set(blockchain.yield_nodes()) == {node6, node5, node3, node4, node2, node1}
    assert set(blockchain.yield_nodes(block_number=5)) == {node6, node5, node3, node4, node2, node1}
    assert set(blockchain.yield_nodes(block_number=4)) == {node5, node3, node4, node2, node1}
    assert set(blockchain.yield_nodes(block_number=3)) == {node3, node4, node2, node1}
    assert set(blockchain.yield_nodes(block_number=2)) == {node4, node3_old, node2, node1}
    assert set(blockchain.yield_nodes(block_number=1)) == {node3_old, node2, node1}
    assert set(blockchain.yield_nodes(block_number=0)) == {node2, node1}
    assert set(blockchain.yield_nodes(block_number=-1)) == {node1}
