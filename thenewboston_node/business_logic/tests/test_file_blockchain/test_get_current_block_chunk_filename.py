from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.tests.factories import add_blocks


def test_get_current_block_chunk_filename_based_on_blockchain_state(file_blockchain: FileBlockchain):
    assert file_blockchain.get_blockchain_state_count() == 1
    assert file_blockchain.get_last_blockchain_state().last_block_number == -1
    assert file_blockchain.get_current_block_chunk_filename(
    ) == '00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'


def test_get_current_block_chunk_filename_does_not_change_if_snapshot_is_not_added(file_blockchain: FileBlockchain):
    assert file_blockchain.get_blockchain_state_count() == 1
    assert file_blockchain.get_last_blockchain_state().last_block_number == -1
    assert file_blockchain.get_current_block_chunk_filename(
    ) == '00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'

    file_blockchain.snapshot_blockchain_state()
    assert file_blockchain.get_blockchain_state_count() == 1
    assert file_blockchain.get_last_blockchain_state().last_block_number == -1
    assert file_blockchain.get_current_block_chunk_filename(
    ) == '00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'


def test_get_current_block_chunk_filename_changes_when_snapshot_is_added(file_blockchain: FileBlockchain):
    assert file_blockchain.get_blockchain_state_count() == 1
    assert file_blockchain.get_last_blockchain_state().last_block_number == -1
    assert file_blockchain.get_current_block_chunk_filename(
    ) == '00000000000000000000-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'

    add_blocks(
        file_blockchain,
        1,
        signing_key=file_blockchain._test_primary_validator_key_pair.private  # type: ignore
    )  # type: ignore
    file_blockchain.snapshot_blockchain_state()
    assert file_blockchain.get_blockchain_state_count() == 2
    assert file_blockchain.get_last_blockchain_state().last_block_number == 0
    assert file_blockchain.get_current_block_chunk_filename(
    ) == '00000000000000000001-xxxxxxxxxxxxxxxxxxxx-block-chunk.msgpack'
