from dataclasses import dataclass
from enum import Enum, unique

from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring

from .mixins.compactable import CompactableMixin
from .mixins.documentable import DocumentableMixin
from .mixins.misc import HumanizedClassNameMixin


@unique
class BlockType(Enum):
    COIN_TRANSFER = 'ct'
    NODE_DECLARATION = 'nd'


def get_request_to_block_type_map():
    from thenewboston_node.business_logic.algorithms.updated_account_states import (
        get_updated_account_states_for_coin_transfer, get_updated_account_states_for_node_declaration
    )

    from .signed_change_request import CoinTransferSignedChangeRequest, NodeDeclarationSignedChangeRequest
    return {
        CoinTransferSignedChangeRequest: (BlockType.COIN_TRANSFER.value, get_updated_account_states_for_coin_transfer),
        NodeDeclarationSignedChangeRequest:
            (BlockType.NODE_DECLARATION.value, get_updated_account_states_for_node_declaration),
    }


def get_signed_change_request_type(block_type):
    for signed_change_request_class, (item_block_type, _) in get_request_to_block_type_map().items():
        if item_block_type == block_type:
            return signed_change_request_class


@revert_docstring
@dataclass
@cover_docstring
class BaseDataclass(CompactableMixin, HumanizedClassNameMixin, DocumentableMixin):
    pass
