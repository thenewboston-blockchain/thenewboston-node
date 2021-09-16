import copy
from contextlib import contextmanager

from django.test import override_settings

from thenewboston_node.business_logic.blockchain.base import BlockchainBase


@contextmanager
def force_blockchain(blockchain):
    try:
        BlockchainBase.set_instance_cache(blockchain)
        yield
    finally:
        BlockchainBase.clear_instance_cache()


def force_node_key(signing_key):
    return override_settings(NODE_SIGNING_KEY=signing_key)


def force_node_fee(fee_amount):
    return override_settings(NODE_FEE_AMOUNT=fee_amount)


def remove_meta(obj):
    obj_copy = copy.copy(obj)
    obj_copy.meta = None
    return obj_copy


def assert_blockchain_content(blockchain: BlockchainBase, blockchain_state_block_numbers, blockchain_block_numbers):
    assert tuple(
        bs.last_block_number for bs in blockchain.yield_blockchain_states()  # type: ignore
    ) == blockchain_state_block_numbers
    assert tuple(bl.get_block_number() for bl in blockchain.yield_blocks()) == blockchain_block_numbers


def assert_iter_equal_except_meta(iter1, iter2, negate=False):
    tuple1 = tuple(remove_meta(obj) for obj in iter1)
    tuple2 = tuple(remove_meta(obj) for obj in iter2)
    if negate:
        assert tuple1 != tuple2
    else:
        assert tuple1 == tuple2


def assert_blockchain_tail_match(blockchain1: BlockchainBase, blockchain2: BlockchainBase):
    assert remove_meta(blockchain1.get_last_blockchain_state()) == remove_meta(blockchain2.get_last_blockchain_state())

    blockchain1_tail_blocks = tuple(blockchain1.yield_blocks_till_snapshot())
    blockchain2_tail_blocks = tuple(blockchain2.yield_blocks_till_snapshot())

    assert tuple(bl.get_block_number() for bl in blockchain1_tail_blocks
                 ) == tuple(bl.get_block_number() for bl in blockchain2_tail_blocks)
    assert_iter_equal_except_meta(blockchain1_tail_blocks, blockchain2_tail_blocks)


def assert_blockchains_equal(blockchain1: BlockchainBase, blockchain2: BlockchainBase, negate=False):
    # blockchain states
    blockchain1_block_states = tuple(blockchain1.yield_blockchain_states())
    blockchain2_block_states = tuple(blockchain2.yield_blockchain_states())

    tuple1 = tuple(bs.last_block_number for bs in blockchain1_block_states)  # type: ignore
    tuple2 = tuple(bs.last_block_number for bs in blockchain2_block_states)  # type: ignore
    if negate:
        assert tuple1 != tuple2
    else:
        assert tuple1 == tuple2

    assert_iter_equal_except_meta(blockchain1_block_states, blockchain2_block_states, negate=negate)

    # blocks
    blockchain1_blocks = tuple(blockchain1.yield_blocks())
    blockchain2_blocks = tuple(blockchain2.yield_blocks())

    tuple1 = tuple(bl.get_block_number() for bl in blockchain1_blocks)
    tuple2 = tuple(bl.get_block_number() for bl in blockchain2_blocks)
    if negate:
        assert tuple1 != tuple2
    else:
        assert tuple1 == tuple2

    assert_iter_equal_except_meta(blockchain1_blocks, blockchain2_blocks, negate=negate)
