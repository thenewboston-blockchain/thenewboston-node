from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.models import AccountState, Block, Node, NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.tests.baker_factories import baker
from thenewboston_node.core.utils.cryptography import generate_key_pair


def test_can_get_nodes_empty_list(blockchain_directory, blockchain_genesis_state):
    blockchain = FileBlockchain(base_directory=blockchain_directory)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    assert blockchain.get_nodes() == []


def test_can_get_nodes_single_node_from_blockchain_genesis_state(
    blockchain_directory, blockchain_genesis_state, user_account_key_pair
):
    blockchain = FileBlockchain(base_directory=blockchain_directory)

    account_number = user_account_key_pair.public
    node = baker.make(Node, identifier=account_number)
    blockchain_genesis_state.account_states[account_number] = AccountState(node=node)

    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    assert blockchain.get_nodes() == [node]


def test_can_get_nodes_single_node_from_blocks(blockchain_directory, blockchain_genesis_state, user_account_key_pair):
    blockchain = FileBlockchain(base_directory=blockchain_directory)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://127.0.0.1:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    node = request.message.node
    assert node.identifier

    block = Block.create_from_signed_change_request(blockchain, request)
    blockchain.add_block(block)

    assert blockchain.get_nodes() == [node]


def test_can_get_nodes_from_genesis_state_and_blocks(
    blockchain_directory, blockchain_genesis_state, user_account_key_pair
):
    blockchain = FileBlockchain(base_directory=blockchain_directory)

    key_pair = generate_key_pair()
    blockchain_state_node = baker.make(Node, identifier=key_pair.public)
    blockchain_genesis_state.account_states[key_pair.public] = AccountState(node=blockchain_state_node)

    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://127.0.0.1:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    blocks_node = request.message.node
    assert blocks_node.identifier

    block = Block.create_from_signed_change_request(blockchain, request)
    blockchain.add_block(block)

    assert blockchain.get_nodes() == [blocks_node, blockchain_state_node]


def test_can_get_nodes_blocks_node_overrides_genesis_state_node(
    blockchain_directory, blockchain_genesis_state, user_account_key_pair
):
    blockchain = FileBlockchain(base_directory=blockchain_directory)

    account_number = user_account_key_pair.public
    blockchain_state_node = baker.make(
        Node, network_addresses=['https://192.168.0.32:8555/'], identifier=account_number
    )
    blockchain_genesis_state.account_states[account_number] = AccountState(node=blockchain_state_node)

    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://127.0.0.1:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    blocks_node = request.message.node
    assert blocks_node.identifier

    block = Block.create_from_signed_change_request(blockchain, request)
    blockchain.add_block(block)

    assert blocks_node != blockchain_state_node
    assert blockchain.get_nodes() == [blocks_node]


def test_can_get_nodes_from_different_block_numbers(
    blockchain_directory, blockchain_genesis_state, user_account_key_pair
):
    account_number = user_account_key_pair.public

    blockchain = FileBlockchain(base_directory=blockchain_directory)
    blockchain_state_node = baker.make(
        Node, network_addresses=['https://192.168.0.29:8555/'], identifier=account_number
    )
    blockchain_genesis_state.account_states[account_number] = AccountState(node=blockchain_state_node)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.30:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    node0 = request.message.node

    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.31:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )

    node1 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.32:8555/'], fee_amount=3, signing_key=user_account_key_pair.private
    )
    node2 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    assert blockchain.get_nodes() == [node2]
    assert blockchain.get_nodes(block_number=2) == [node2]
    assert blockchain.get_nodes(block_number=1) == [node1]
    assert blockchain.get_nodes(block_number=0) == [node0]
    assert blockchain.get_nodes(block_number=-1) == [blockchain_state_node]


def test_can_get_nodes_from_complex_blockchain(blockchain_directory, blockchain_genesis_state):
    key_pair1 = generate_key_pair()
    key_pair2 = generate_key_pair()
    key_pair3 = generate_key_pair()
    key_pair4 = generate_key_pair()
    key_pair5 = generate_key_pair()
    key_pair6 = generate_key_pair()
    assert len({
        key_pair1.public, key_pair2.public, key_pair3.public, key_pair4.public, key_pair5.public, key_pair6.public
    }) == 6

    blockchain = FileBlockchain(base_directory=blockchain_directory)
    node1 = baker.make(Node, network_addresses=['https://192.168.0.29:8555/'], identifier=key_pair1.public)
    blockchain_genesis_state.account_states[node1.identifier] = AccountState(node=node1)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    # Block 0
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.30:8555/'], fee_amount=3, signing_key=key_pair2.private
    )
    node2 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    # Block 1
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.31:8555/'], fee_amount=3, signing_key=key_pair3.private
    )
    node3_old = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    # Block 2
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.32:8555/'], fee_amount=3, signing_key=key_pair4.private
    )
    node4 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    def sort_key(value):
        return value.network_addresses

    def sort_me(list_):
        return sorted(list_, key=sort_key)

    assert sort_me(blockchain.get_nodes(block_number=2)) == sort_me([node4, node3_old, node2, node1])

    blockchain.snapshot_blockchain_state()

    # Block 3
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.33:8555/'], fee_amount=3, signing_key=key_pair3.private
    )
    node3 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    # Block 4
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.34:8555/'], fee_amount=3, signing_key=key_pair5.private
    )
    node5 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    # Block 5
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://192.168.0.35:8555/'], fee_amount=3, signing_key=key_pair6.private
    )
    node6 = request.message.node
    blockchain.add_block(Block.create_from_signed_change_request(blockchain, request))

    assert sort_me(blockchain.get_nodes()) == sort_me([node6, node5, node3, node4, node2, node1])
    assert sort_me(blockchain.get_nodes(block_number=5)) == sort_me([node6, node5, node3, node4, node2, node1])
    assert sort_me(blockchain.get_nodes(block_number=4)) == sort_me([node5, node3, node4, node2, node1])
    assert sort_me(blockchain.get_nodes(block_number=3)) == sort_me([node3, node4, node2, node1])
    assert sort_me(blockchain.get_nodes(block_number=2)) == sort_me([node4, node3_old, node2, node1])
    assert sort_me(blockchain.get_nodes(block_number=1)) == sort_me([node3_old, node2, node1])
    assert sort_me(blockchain.get_nodes(block_number=0)) == sort_me([node2, node1])
    assert sort_me(blockchain.get_nodes(block_number=-1)) == sort_me([node1])
