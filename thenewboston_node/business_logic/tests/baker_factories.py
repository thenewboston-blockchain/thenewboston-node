from thenewboston_node.business_logic.models import Block, BlockMessage
from thenewboston_node.business_logic.models.signed_change_request import SIGNED_CHANGE_REQUEST_TYPE_MAP
from thenewboston_node.business_logic.models.signed_change_request.constants import BlockType
from thenewboston_node.core.utils import baker


def make_block(block_type, **kwargs):
    if 'message' not in kwargs:
        request_class = SIGNED_CHANGE_REQUEST_TYPE_MAP.get(block_type)
        if not request_class:
            raise NotImplementedError(f'Block type {block_type} is not supported yet')

        signed_change_request = baker.make(request_class)
        message = baker.make(BlockMessage, block_type=block_type, signed_change_request=signed_change_request)
        for account_number, account_state in message.updated_account_states.items():
            account_state.node.identifier = account_number

        kwargs['message'] = message

    return baker.make(Block, **kwargs)


def make_coin_transfer_block(**kwargs):
    return make_block(block_type=BlockType.COIN_TRANSFER.value, **kwargs)


def make_node_declaration_block(**kwargs):
    return make_block(block_type=BlockType.NODE_DECLARATION.value, **kwargs)
