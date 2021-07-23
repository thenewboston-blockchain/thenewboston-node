import os.path

import pytest

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.cryptography import KeyPair


@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_blockchain_state_is_created_every_x_block(
    blockchain_path,
    blockchain_genesis_state,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
):
    assert not os.path.isfile(
        str(blockchain_path / 'blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack')
    )
    blockchain = FileBlockchain(
        base_directory=str(blockchain_path),
        snapshot_period_in_blocks=5,
        account_root_files_subdir='blockchain-states',
        account_root_files_storage_kwargs={'compressors': ()}
    )
    blockchain.add_blockchain_state(blockchain_genesis_state)
    assert os.path.isfile(
        str(blockchain_path / 'blockchain-states/0/0/0/0/0/0/0/0/000000000!-blockchain-state.msgpack')
    )
    blockchain.validate()

    user_account = user_account_key_pair.public

    for _ in range(4):
        block = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=30,
            request_signing_key=treasury_account_key_pair.private,
            pv_signing_key=get_node_signing_key(),
        )
        assert not os.path.isfile(
            str(
                blockchain_path /
                f'blockchain-states/0/0/0/0/0/0/0/0/000000000{block.message.block_number}-blockchain-state.msgpack'
            )
        )
        blockchain.add_block(block)

    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=30,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
    )
    blockchain.add_block(block)
    assert os.path.isfile(
        str(
            blockchain_path /
            f'blockchain-states/0/0/0/0/0/0/0/0/000000000{block.message.block_number}-blockchain-state.msgpack'
        )
    )

    for _ in range(4):
        block = Block.create_from_main_transaction(
            blockchain=blockchain,
            recipient=user_account,
            amount=30,
            request_signing_key=treasury_account_key_pair.private,
            pv_signing_key=get_node_signing_key(),
        )
        assert not os.path.isfile(
            str(
                blockchain_path /
                f'blockchain-states/0/0/0/0/0/0/0/0/000000000{block.message.block_number}-blockchain-state.msgpack'
            )
        )
        blockchain.add_block(block)

    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account,
        amount=30,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
    )
    blockchain.add_block(block)
    assert os.path.isfile(
        str(
            blockchain_path /
            f'blockchain-states/0/0/0/0/0/0/0/0/000000000{block.message.block_number}-blockchain-state.msgpack'
        )
    )
