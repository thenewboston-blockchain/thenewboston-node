from django.test import override_settings

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.tests.base import assert_blockchains_equal
from thenewboston_node.business_logic.tests.factories import add_blocks


def test_can_copy_from(
    blockchain_directory, blockchain_directory2, treasury_account_key_pair, user_account_key_pair,
    primary_validator_key_pair
):
    assert blockchain_directory != blockchain_directory2

    source = FileBlockchain(base_directory=blockchain_directory, snapshot_period_in_blocks=10)
    with override_settings(NODE_SIGNING_KEY=primary_validator_key_pair.private):
        add_blocks(
            source,
            35,
            treasury_account_key_pair.private,
            add_blockchain_genesis_state=True,
            signing_key=primary_validator_key_pair.private
        )

    target = FileBlockchain(base_directory=blockchain_directory2, snapshot_period_in_blocks=10)
    with override_settings(NODE_SIGNING_KEY=primary_validator_key_pair.private):
        add_blocks(
            target,
            58,
            user_account_key_pair.private,
            add_blockchain_genesis_state=True,
            signing_key=primary_validator_key_pair.private
        )
    assert_blockchains_equal(source, target, negate=True)

    target.copy_from(source)
    assert_blockchains_equal(source, target)

    assert list(target.get_blockchain_state_storage().list_directory()) == [
        '0000000000000000000!-blockchain-state.msgpack',
        '00000000000000000009-blockchain-state.msgpack',
        '00000000000000000019-blockchain-state.msgpack',
        '00000000000000000029-blockchain-state.msgpack',
    ]
    assert list(target.get_block_chunk_storage().list_directory()) == [
        '00000000000000000000-00000000000000000009-block-chunk.msgpack',
        '00000000000000000010-00000000000000000019-block-chunk.msgpack',
        '00000000000000000020-00000000000000000029-block-chunk.msgpack',
        '00000000000000000030-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack',
    ]
