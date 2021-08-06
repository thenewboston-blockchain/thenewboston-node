import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.cryptography import KeyPair


@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_validate_blockchain(
    memory_blockchain: MemoryBlockchain,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
):
    user_account = user_account_key_pair.public
    treasury_account = treasury_account_key_pair.public

    blockchain = memory_blockchain
    blockchain.validate(is_partial_allowed=False)

    block0 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=30,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
    )
    blockchain.add_block(block0)
    blockchain.snapshot_blockchain_state()
    blockchain.validate(is_partial_allowed=False)

    block1 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=10,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
    )
    blockchain.add_block(block1)
    blockchain.snapshot_blockchain_state()
    blockchain.validate(is_partial_allowed=False)

    block2 = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=treasury_account,
        amount=10,
        request_signing_key=user_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
    )
    blockchain.add_block(block2)
    blockchain.snapshot_blockchain_state()
    blockchain.validate(is_partial_allowed=False)


@pytest.mark.skip('Not implemented yet')
def test_can_validate_blockchain_in_chunks():
    raise NotImplementedError()
