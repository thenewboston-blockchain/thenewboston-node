import copy

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.tests.factories import add_blocks
from thenewboston_node.business_logic.utils.blockchain import sync_minimal


def remove_meta(obj):
    obj_copy = copy.copy(obj)
    obj_copy.meta = None
    return obj_copy


def assert_blockchain_content(blockchain: BlockchainBase, blockchain_state_block_numbers, blockchain_block_numbers):
    assert tuple(
        bs.last_block_number for bs in blockchain.yield_blockchain_states()  # type: ignore
    ) == blockchain_state_block_numbers
    assert tuple(bl.get_block_number() for bl in blockchain.yield_blocks()) == blockchain_block_numbers


def assert_iter_equal_except_meta(iter1, iter2):
    assert tuple(remove_meta(obj1) for obj1 in iter1) == tuple(remove_meta(obj2) for obj2 in iter2)


def assert_blockchain_tail_match(blockchain1: BlockchainBase, blockchain2: BlockchainBase):
    assert remove_meta(blockchain1.get_last_blockchain_state()) == remove_meta(blockchain2.get_last_blockchain_state())

    blockchain1_tail_blocks = tuple(blockchain1.yield_blocks_till_snapshot())
    blockchain2_tail_blocks = tuple(blockchain2.yield_blocks_till_snapshot())

    assert tuple(bl.get_block_number() for bl in blockchain1_tail_blocks
                 ) == tuple(bl.get_block_number() for bl in blockchain2_tail_blocks)
    assert_iter_equal_except_meta(blockchain1_tail_blocks, blockchain2_tail_blocks)


def assert_blockchains_equal(blockchain1: BlockchainBase, blockchain2: BlockchainBase):
    blockchain1_block_states = tuple(blockchain1.yield_blockchain_states())
    blockchain2_block_states = tuple(blockchain2.yield_blockchain_states())

    assert tuple(bs.last_block_number for bs in blockchain1_block_states  # type: ignore
                 ) == tuple(bs.last_block_number for bs in blockchain2_block_states)  # type: ignore
    assert_iter_equal_except_meta(blockchain1_block_states, blockchain2_block_states)

    blockchain1_blocks = tuple(blockchain1.yield_blocks())
    blockchain2_blocks = tuple(blockchain2.yield_blocks())

    assert tuple(bl.get_block_number() for bl in blockchain1_blocks
                 ) == tuple(bl.get_block_number() for bl in blockchain2_blocks)
    assert_iter_equal_except_meta(blockchain1_blocks, blockchain2_blocks)


def make_synced_blockchains(
    *, blocks_count, treasury_account_private_key, blockchain1_directory, blockchain2_directory
):
    blockchain1 = FileBlockchain(base_directory=blockchain1_directory)
    add_blocks(blockchain1, blocks_count, treasury_account_private_key, add_blockchain_genesis_state=True)
    if blockchain1.get_blockchain_state_count() > 1:
        raise NotImplementedError('Making synced blockchains with more then 1 blockchain states is not implemented')

    assert_blockchain_content(blockchain1, (-1,), tuple(range(blocks_count)))

    blockchain2 = FileBlockchain(base_directory=blockchain2_directory)
    blockchain2.add_blockchain_state(blockchain1.get_first_blockchain_state())
    assert_blockchain_content(blockchain2, (-1,), ())
    for block in blockchain1.yield_blocks():
        blockchain2.add_block(block)

    assert_blockchain_content(blockchain2, (-1,), tuple(range(blocks_count)))
    assert_blockchains_equal(blockchain1, blockchain2)

    return blockchain1, blockchain2


def test_insync_source_and_target_with_one_blockchain_state_and_no_blocks(
    blockchain_directory, blockchain_directory2, treasury_account_key_pair
):
    # Prepare source and target blockchains: genesis state(-1)
    source, target = make_synced_blockchains(
        blocks_count=0,
        treasury_account_private_key=treasury_account_key_pair.private,
        blockchain1_directory=blockchain_directory,
        blockchain2_directory=blockchain_directory2,
    )
    assert_blockchain_content(source, (-1,), ())
    assert_blockchain_content(target, (-1,), ())
    assert_blockchains_equal(source, target)

    # Sync blockchains
    sync_minimal(source, target)

    # Expect target blockchain: blockchain state(-1)
    assert_blockchain_content(target, (-1,), ())
    assert_blockchain_tail_match(source, target)
    assert_blockchains_equal(source, target)


def test_source_one_block_different_than_target(
    blockchain_directory, blockchain_directory2, treasury_account_key_pair
):
    # Prepare source and target blockchains: genesis state(-1)
    source, target = make_synced_blockchains(
        blocks_count=0,
        treasury_account_private_key=treasury_account_key_pair.private,
        blockchain1_directory=blockchain_directory,
        blockchain2_directory=blockchain_directory2,
    )
    assert_blockchain_content(source, (-1,), ())
    assert_blockchain_content(target, (-1,), ())
    assert_blockchains_equal(source, target)

    add_blocks(source, 1, treasury_account_key_pair.private)
    assert_blockchain_content(source, (-1,), (0,))

    # Sync blockchains
    sync_minimal(source, target)

    # Expect target blockchain: blockchain state(-1) + 1 block(0)
    assert_blockchain_content(target, (-1,), (0,))
    assert_blockchain_tail_match(source, target)
    assert_blockchains_equal(source, target)


def test_source_has_more_blocks_than_target(blockchain_directory, blockchain_directory2, treasury_account_key_pair):
    # Prepare source and target blockchains: genesis state(-1) + 3 blocks(0, 1, 2)
    source, target = make_synced_blockchains(
        blocks_count=3,
        treasury_account_private_key=treasury_account_key_pair.private,
        blockchain1_directory=blockchain_directory,
        blockchain2_directory=blockchain_directory2,
    )
    assert_blockchain_content(source, (-1,), (0, 1, 2))
    assert_blockchain_content(target, (-1,), (0, 1, 2))
    assert_blockchains_equal(source, target)

    # Update source with 2 more blocks: genesis state(-1) + 5 blocks(0, 1, 2, 3, 4)
    add_blocks(source, 2, treasury_account_key_pair.private)
    assert_blockchain_content(source, (-1,), (0, 1, 2, 3, 4))

    # Sync blockchains
    sync_minimal(source, target)

    # Expect target blockchain: genesis state(-1) + 5 blocks(0, 1, 2, 3, 4)
    assert_blockchain_content(target, (-1,), (0, 1, 2, 3, 4))
    assert_blockchain_tail_match(source, target)
    assert_blockchains_equal(source, target)


def test_source_one_block_and_blockchain_state_different_than_target(
    blockchain_directory, blockchain_directory2, treasury_account_key_pair
):
    # Prepare source and target blockchains: genesis state(-1) + 1 block(0) + blockchain state(0)
    source, target = make_synced_blockchains(
        blocks_count=0,
        treasury_account_private_key=treasury_account_key_pair.private,
        blockchain1_directory=blockchain_directory,
        blockchain2_directory=blockchain_directory2,
    )
    assert_blockchain_content(source, (-1,), ())
    assert_blockchain_content(target, (-1,), ())
    assert_blockchains_equal(source, target)

    # Update source with 1 more block and a blockchain state: genesis state(-1) + 1 block(0) + genesis state(0)
    add_blocks(source, 1, treasury_account_key_pair.private)
    source.snapshot_blockchain_state()
    assert_blockchain_content(source, (-1, 0), (0,))

    # Sync blockchains
    sync_minimal(source, target)

    # Expect target blockchain: blockchain state(0)
    assert_blockchain_content(target, (0,), ())
    assert_blockchain_tail_match(source, target)


def test_insync_blockchains_ending_with_blockchain_state(
    blockchain_directory, blockchain_directory2, treasury_account_key_pair
):
    # Prepare source and target
    source, target = make_synced_blockchains(
        blocks_count=15,
        treasury_account_private_key=treasury_account_key_pair.private,
        blockchain1_directory=blockchain_directory,
        blockchain2_directory=blockchain_directory2,
    )
    assert_blockchain_content(source, (-1,), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    assert_blockchain_content(target, (-1,), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    assert_blockchains_equal(source, target)

    # Update blockchains with a blockchain state
    source.snapshot_blockchain_state()
    target.snapshot_blockchain_state()
    assert_blockchain_content(target, (-1, 14), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    assert_blockchains_equal(source, target)

    # Sync blockchains
    sync_minimal(source, target)

    # Expect
    assert_blockchain_content(target, (-1, 14), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    assert_blockchain_tail_match(source, target)
    assert_blockchains_equal(source, target)


def test_insync_blockchains_ending_with_blocks(blockchain_directory, blockchain_directory2, treasury_account_key_pair):
    # Prepare source and target
    source, target = make_synced_blockchains(
        blocks_count=15,
        treasury_account_private_key=treasury_account_key_pair.private,
        blockchain1_directory=blockchain_directory,
        blockchain2_directory=blockchain_directory2,
    )
    assert_blockchain_content(source, (-1,), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    assert_blockchain_content(target, (-1,), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    assert_blockchains_equal(source, target)

    source.snapshot_blockchain_state()
    target.snapshot_blockchain_state()
    assert_blockchain_content(target, (-1, 14), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
    assert_blockchains_equal(source, target)

    # Add 3 more blocks
    add_blocks(source, 3, treasury_account_key_pair.private)
    assert_blockchain_content(source, (-1, 14), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17))
    for block in source.yield_blocks_from(15):
        target.add_block(block)
    assert_blockchain_content(target, (-1, 14), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17))
    assert_blockchains_equal(source, target)

    # Sync blockchains
    sync_minimal(source, target)

    # Expect
    assert_blockchain_content(target, (-1, 14), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17))
    assert_blockchain_tail_match(source, target)
    assert_blockchains_equal(source, target)


def test_sync_source_has_blocks_after_blockchain_state_with_gap(
    blockchain_directory, blockchain_directory2, treasury_account_key_pair
):
    # Prepare source and target blockchains: genesis state(-1) + 3 blocks(0-2)
    source, target = make_synced_blockchains(
        blocks_count=3,
        treasury_account_private_key=treasury_account_key_pair.private,
        blockchain1_directory=blockchain_directory,
        blockchain2_directory=blockchain_directory2,
    )
    assert_blockchain_content(source, (-1,), (0, 1, 2))
    assert_blockchain_content(target, (-1,), (0, 1, 2))
    assert_blockchains_equal(source, target)

    # Update source blockchain: genesis state(-1) + 15 blocks(0-14) + blockchain state(14) + 3 blocks(15-17)
    source = FileBlockchain(base_directory=blockchain_directory)
    add_blocks(source, 12, treasury_account_key_pair.private)
    source.snapshot_blockchain_state()
    add_blocks(source, 3, treasury_account_key_pair.private)
    assert_blockchain_content(source, (-1, 14), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17))

    # Sync blockchains
    sync_minimal(source, target)

    # Expect target blockchain: blockchain state(1) | 3 blocks(15-17)
    assert_blockchain_content(target, (14,), (15, 16, 17))
    assert_blockchain_tail_match(source, target)
