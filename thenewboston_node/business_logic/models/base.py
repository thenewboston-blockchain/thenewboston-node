from enum import Enum, unique

from .signed_change_request import CoinTransferSignedChangeRequest, NodeDeclarationSignedChangeRequest


@unique
class BlockType(Enum):
    COIN_TRANSFER = 'ct'
    NETWORK_ADDRESS_REGISTRATION = 'ar'


def get_request_to_block_type_map():
    from thenewboston_node.business_logic.algorithms.updated_account_states import (
        get_updated_account_states_for_coin_transfer, get_updated_account_states_for_node_declaration
    )

    return {
        CoinTransferSignedChangeRequest: (BlockType.COIN_TRANSFER.value, get_updated_account_states_for_coin_transfer),
        NodeDeclarationSignedChangeRequest:
            (BlockType.NETWORK_ADDRESS_REGISTRATION.value, get_updated_account_states_for_node_declaration),
    }
