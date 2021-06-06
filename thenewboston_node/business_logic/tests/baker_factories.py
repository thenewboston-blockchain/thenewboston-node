from thenewboston_node.business_logic.models import Block, BlockMessage, CoinTransferSignedChangeRequest
from thenewboston_node.core.utils import baker


def make_block(block_type, **kwargs):
    if 'message' not in kwargs:
        if block_type == 'ct':
            signed_change_request = baker.make(CoinTransferSignedChangeRequest)
        else:
            raise NotImplementedError(f'Block type {block_type} is not supported yet')

        message = baker.make(BlockMessage, block_type=block_type, signed_change_request=signed_change_request)
        for account_number, account_state in message.updated_account_states.items():
            account_state.node.identifier = account_number

        kwargs['message'] = message

    return baker.make(Block, **kwargs)


def make_coin_transfer_block(**kwargs):
    return make_block(block_type='ct', **kwargs)
