from dataclasses import dataclass

from thenewboston_node.business_logic.models import (
    AccountState, Block, BlockMessage, Node, SignedChangeRequest, SignedChangeRequestMessage
)
from thenewboston_node.business_logic.models.mixins.documentable import DocumentableMixin


def test_get_nested_models():
    assert set(Block.get_nested_models(include_self=True)
               ) == {Block, BlockMessage, SignedChangeRequest, AccountState, Node, SignedChangeRequestMessage}


def test_get_field_docstring():

    @dataclass
    class TestDataclass(DocumentableMixin):
        field_with_explicit_docstring: int
        """A docstring"""

        field_with_implicit_docstring: int

    assert TestDataclass.get_field_docstring('field_with_explicit_docstring') == 'A docstring'
    assert TestDataclass.get_field_docstring('field_with_implicit_docstring') == 'Field with implicit docstring'
