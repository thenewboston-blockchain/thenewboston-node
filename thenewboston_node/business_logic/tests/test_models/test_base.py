from thenewboston_node.business_logic.models import Block, BlockchainState
from thenewboston_node.business_logic.models.mixins.compactable import COMPACT_KEY_MAP
from thenewboston_node.core.utils import baker

COMPACTED_KEYS = set(COMPACT_KEY_MAP.values())


def assert_key_compacted(key):
    assert key in COMPACTED_KEYS
    assert key not in COMPACT_KEY_MAP


def assert_dict_compacted(dict_):
    for key, value in dict_.items():
        if isinstance(key, str):
            assert_key_compacted(key)

        if isinstance(value, dict):
            assert_dict_compacted(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    assert_dict_compacted(item)


def test_all_block_keys_are_compacted():
    block = baker.make(Block)
    compacted_dict = block.to_compact_dict()
    assert_dict_compacted(compacted_dict)


def test_all_blockchain_state_keys_are_compacted():
    blockchain_state = baker.make(BlockchainState)
    compacted_dict = blockchain_state.to_compact_dict()
    assert_dict_compacted(compacted_dict)
