from thenewboston_node.business_logic.tests import baker_factories


def test_meta_attribute_does_not_serialize():
    block = baker_factories.make_coin_transfer_block(meta=None)

    compacted = block.to_compact_dict()
    assert 'meta' not in compacted
