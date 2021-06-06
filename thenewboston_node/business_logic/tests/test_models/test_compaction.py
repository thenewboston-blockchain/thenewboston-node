import typing

from thenewboston_node.business_logic.models import BlockchainState
from thenewboston_node.business_logic.models.base import BlockType
from thenewboston_node.business_logic.models.mixins.compactable import COMPACT_KEY_MAP, bytes_to_hex
from thenewboston_node.business_logic.models.mixins.compactable import compact_key as ck
from thenewboston_node.business_logic.models.mixins.serializable import SerializableMixin
from thenewboston_node.business_logic.tests import baker_factories
from thenewboston_node.core.utils import baker
from thenewboston_node.core.utils.types import hexstr

COMPACTED_KEYS = set(COMPACT_KEY_MAP.values())
SENTINEL = object()


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


def assert_instance_is_binarized(instance, dict_):  # noqa: C901
    for field_name in instance.get_field_names():
        dict_value = dict_.get(ck(field_name), SENTINEL)
        if dict_value is SENTINEL:
            continue

        instance_value = getattr(instance, field_name)
        field_type = instance.get_field_type(field_name)
        if issubclass(field_type, SerializableMixin):
            assert_instance_is_binarized(instance_value, dict_value)
        else:
            origin = typing.get_origin(field_type)
            if origin and issubclass(origin, list):
                (item_type,) = typing.get_args(field_type)
                for index, item in enumerate(dict_value):
                    if issubclass(item_type, SerializableMixin):
                        assert_instance_is_binarized(instance_value[index], item)
                    elif issubclass(item_type, hexstr):
                        assert isinstance(item, bytes), f'{item} of {field_name} is not binarized'
            if origin and issubclass(origin, dict):
                (item_key_type, item_value_type) = typing.get_args(field_type)
                for item_key, item_value in dict_value.items():
                    if issubclass(item_key_type, hexstr):
                        assert isinstance(item_key, bytes), f'{item_key} of {field_name} is not binarized'

                    instance_item_key = bytes_to_hex(item_key) if isinstance(item_key, bytes) else item_key
                    if issubclass(item_value_type, SerializableMixin):
                        assert_instance_is_binarized(instance_value[instance_item_key], item_value)
                    elif issubclass(item_value_type, hexstr):
                        assert isinstance(item_value,
                                          bytes), (f'{item_value} of {item_key} key of {field_name} is not binarized')
            elif issubclass(field_type, hexstr):
                assert isinstance(dict_value, bytes), f'{field_name} of {instance} is not binarized'


def test_all_block_keys_are_compacted():
    for block_type in BlockType:
        block = baker_factories.make_block(block_type.value)
        compacted_dict = block.to_compact_dict()
        assert_dict_compacted(compacted_dict)


def test_all_blockchain_state_keys_are_compacted():
    blockchain_state = baker.make(BlockchainState)
    compacted_dict = blockchain_state.to_compact_dict()
    assert_dict_compacted(compacted_dict)


def test_all_hexadecimals_are_binarized():
    for block_type in BlockType:
        block = baker_factories.make_block(block_type.value)
        compacted_dict = block.to_compact_dict()
        assert_instance_is_binarized(block, compacted_dict)
