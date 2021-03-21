from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.block_message import BlockMessage


def make_block(node_identifier=None, message=None, message_hash=None, message_signature=None):
    return Block(
        node_identifier=node_identifier,
        message=message,
        message_hash=message_hash,
        message_signature=message_signature
    )


def make_block_message(
    transfer_request=None, timestamp=None, block_identifier=None, block_number=None, updated_balances=None
):
    return BlockMessage(
        transfer_request=transfer_request,
        timestamp=timestamp,
        block_identifier=block_identifier,
        block_number=block_number,
        updated_balances=updated_balances
    )
