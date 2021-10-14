import logging

from celery import shared_task

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.business_logic.models.block_confirmation import BlockConfirmation
from thenewboston_node.business_logic.node import get_node_identifier, get_node_signing_key
from thenewboston_node.core.clients.node import NodeClient
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)


@shared_task
def send_block_confirmation(destination_node_identifier: hexstr, block_number: int):
    blockchain = BlockchainBase.get_instance()
    this_node_role = blockchain.get_node_role(get_node_identifier())
    if this_node_role != NodeRole.CONFIRMATION_VALIDATOR:
        logger.warning('Node must be a confirmation validator to send block confirmations')
        return

    destination_node = blockchain.get_node_by_identifier(destination_node_identifier)
    block = blockchain.get_block_by_number(block_number)
    assert destination_node is not None
    assert block is not None

    block_confirmation = BlockConfirmation.create_from_block(block=block, cv_signing_key=get_node_signing_key())

    node_client = NodeClient.get_instance()
    node_client.send_block_confirmation_to_node(node=destination_node, block_confirmation=block_confirmation)
