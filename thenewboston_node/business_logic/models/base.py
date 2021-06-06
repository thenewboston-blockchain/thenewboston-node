from dataclasses import dataclass
from enum import Enum, unique

from .mixins.compactable import CompactableMixin


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


@dataclass
class BaseDataclass(CompactableMixin):
    pass
