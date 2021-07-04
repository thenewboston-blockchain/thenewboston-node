from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.models import (
    AccountState, Block, Node, NodeDeclarationSignedChangeRequest, PrimaryValidatorSchedule,
    PrimaryValidatorScheduleSignedChangeRequest
)
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.tests.baker_factories import baker
from thenewboston_node.core.utils.cryptography import generate_key_pair


def test_no_pv_schedule(blockchain_directory, blockchain_genesis_state):
    blockchain = FileBlockchain(base_directory=blockchain_directory)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()
    assert blockchain.get_primary_validator() is None
    assert blockchain.get_primary_validator(0) is None
    assert blockchain.get_primary_validator(10) is None


def test_can_get_pv_from_blockchain_genesis_state(
    blockchain_directory, blockchain_genesis_state, user_account_key_pair
):
    blockchain = FileBlockchain(base_directory=blockchain_directory)

    account_number = user_account_key_pair.public
    node = baker.make(Node, identifier=account_number)
    pv_schedule = baker.make(PrimaryValidatorSchedule, begin_block_number=0, end_block_number=99)
    blockchain_genesis_state.account_states[account_number] = AccountState(
        node=node, primary_validator_schedule=pv_schedule
    )

    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    assert blockchain.get_primary_validator() == node
    assert blockchain.get_primary_validator(0) == node
    assert blockchain.get_primary_validator(10) == node
    assert blockchain.get_primary_validator(99) == node
    assert blockchain.get_primary_validator(100) is None


def test_can_get_pv_from_from_blocks(blockchain_directory, blockchain_genesis_state, user_account_key_pair):
    blockchain = FileBlockchain(base_directory=blockchain_directory)
    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    signing_key = user_account_key_pair.private
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['https://127.0.0.1:8555/'], fee_amount=3, signing_key=signing_key
    )
    node = request.message.node
    assert node.identifier

    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())
    blockchain.add_block(block)

    request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, signing_key)
    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == node
    assert blockchain.get_primary_validator(0) == node
    assert blockchain.get_primary_validator(10) == node
    assert blockchain.get_primary_validator(99) == node
    assert blockchain.get_primary_validator(100) is None


def test_can_get_node_from_genesis_state_and_pv_from_blocks(
    blockchain_directory, blockchain_genesis_state, user_account_key_pair
):
    blockchain = FileBlockchain(base_directory=blockchain_directory)

    account_number = user_account_key_pair.public
    node = baker.make(Node, identifier=account_number)
    pv_schedule = baker.make(PrimaryValidatorSchedule, begin_block_number=0, end_block_number=99)
    blockchain_genesis_state.account_states[account_number] = AccountState(
        node=node, primary_validator_schedule=pv_schedule
    )

    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()

    request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, user_account_key_pair.private)
    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == node
    assert blockchain.get_primary_validator(0) == node
    assert blockchain.get_primary_validator(10) == node
    assert blockchain.get_primary_validator(99) == node
    assert blockchain.get_primary_validator(100) is None


def test_can_get_overridden_pv(blockchain_directory, blockchain_genesis_state, user_account_key_pair):
    blockchain = FileBlockchain(base_directory=blockchain_directory)

    account_number = user_account_key_pair.public
    node = baker.make(Node, identifier=account_number)
    pv_schedule = baker.make(PrimaryValidatorSchedule, begin_block_number=0, end_block_number=99)
    blockchain_genesis_state.account_states[account_number] = AccountState(
        node=node, primary_validator_schedule=pv_schedule
    )

    another_key_pair = generate_key_pair()
    another_node = baker.make(Node, identifier=another_key_pair.public)
    blockchain_genesis_state.account_states[another_key_pair.public] = AccountState(node=another_node)

    blockchain.add_blockchain_state(blockchain_genesis_state)
    blockchain.validate()
    assert blockchain.get_primary_validator() == node
    assert blockchain.get_primary_validator(0) == node
    assert blockchain.get_primary_validator(10) == node
    assert blockchain.get_primary_validator(99) == node
    assert blockchain.get_primary_validator(100) is None

    request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, another_key_pair.private)
    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == another_node
    assert blockchain.get_primary_validator(0) == another_node
    assert blockchain.get_primary_validator(10) == another_node
    assert blockchain.get_primary_validator(99) == another_node
    assert blockchain.get_primary_validator(100) is None

    request = PrimaryValidatorScheduleSignedChangeRequest.create(0, 99, user_account_key_pair.private)
    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())
    blockchain.add_block(block)

    assert blockchain.get_primary_validator() == node
    assert blockchain.get_primary_validator(0) == node
    assert blockchain.get_primary_validator(10) == node
    assert blockchain.get_primary_validator(99) == node
    assert blockchain.get_primary_validator(100) is None
