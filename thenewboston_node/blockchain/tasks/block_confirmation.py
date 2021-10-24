import logging

from celery import shared_task

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.node import get_node_identifier, get_node_signing_key
from thenewboston_node.core.clients.node import NodeClient
from thenewboston_node.core.utils.cryptography import derive_public_key, generate_signature, normalize_dict
from thenewboston_node.core.utils.types import hexstr

logger = logging.getLogger(__name__)


@shared_task
def send_block_confirmation(target_node_identifier: hexstr, block_number: int):
    blockchain = BlockchainBase.get_instance()
    target_node = blockchain.get_node_by_identifier(target_node_identifier)
    if target_node is None:
        logger.warning('Node %s is no longer declared', target_node_identifier)
        return

    block = blockchain.get_block_by_number(block_number)
    assert block is not None

    signing_key = get_node_signing_key()
    signer = derive_public_key(signing_key)
    signature = generate_signature(signing_key, normalize_dict(block.serialize_to_dict()))

    node_client = NodeClient.get_instance()
    node_client.send_block_confirmation_to_node(
        node=target_node, block=block, confirmation_signer=signer, confirmation_signature=signature
    )


def start_send_block_confirmation(target_node_identifier: hexstr, block_number: int):
    send_block_confirmation.delay(target_node_identifier=target_node_identifier, block_number=block_number)


@shared_task
def send_block_confirmations(block_number: int):
    blockchain = BlockchainBase.get_instance()
    last_block_number = blockchain.get_last_block_number()
    primary_validator = blockchain.get_primary_validator(block_number)
    assert primary_validator
    exclude = {get_node_identifier(), primary_validator.identifier}

    # TODO(dmu) LOW: Consider running as group: https://docs.celeryproject.org/en/stable/userguide/canvas.html#groups
    for node in blockchain.yield_nodes(last_block_number):
        node_identifier = node.identifier
        if node_identifier in exclude:
            continue

        start_send_block_confirmation(target_node_identifier=node_identifier, block_number=block_number)


def start_send_block_confirmations(block_number: int):
    send_block_confirmations.delay(block_number=block_number)
