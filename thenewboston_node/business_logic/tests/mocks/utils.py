from unittest import mock

from thenewboston_node.business_logic.utils.iter import get_generator


def patch_blockchain_states(blockchain, blockchain_states):
    return mock.patch.object(blockchain, 'yield_blockchain_states', new=get_generator(blockchain_states))


def patch_blocks(blockchain, blocks):
    return mock.patch.object(blockchain, 'yield_blocks', new=get_generator(blocks))
