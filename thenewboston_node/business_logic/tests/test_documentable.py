from thenewboston_node.business_logic.models import (
    AccountState, Block, BlockMessage, Node, SignedChangeRequest, SignedChangeRequestMessage
)


def test_get_nested_models():
    assert set(Block.get_nested_models(include_self=True)
               ) == {Block, BlockMessage, SignedChangeRequest, AccountState, Node, SignedChangeRequestMessage}
