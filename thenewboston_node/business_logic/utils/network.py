import logging

from django.conf import settings

import stun

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import Node
from thenewboston_node.business_logic.node import derive_public_key, get_node_signing_key

logger = logging.getLogger(__name__)


def get_own_network_addresses():
    network_addresses = settings.NODE_NETWORK_ADDRESSES
    if settings.APPEND_AUTO_DETECTED_NETWORK_ADDRESS:
        try:
            logger.info('Detecting external IP address')
            _, external_ip_address, _ = stun.get_ip_info()
            logger.info('External IP address: %s', external_ip_address)
        except Exception:
            logger.warning('Unable to detect external IP address')
        else:
            network_address = f'{settings.NODE_SCHEME}://{external_ip_address}:{settings.NODE_PORT}/'
            network_addresses = list(network_addresses)
            network_addresses.append(network_address)

    return network_addresses


def make_own_node():
    identifier = derive_public_key(get_node_signing_key())
    return Node(
        identifier=identifier,
        network_addresses=get_own_network_addresses(),
        fee_amount=settings.NODE_FEE_AMOUNT,
        fee_account=settings.NODE_FEE_ACCOUNT,
    )


def get_ranked_nodes(blockchain: BlockchainBase):
    # TODO(dmu) HIGH: Implement a more sophisticated ranking algorithm
    nodes = []
    primary_validator = blockchain.get_primary_validator()
    assert primary_validator is not None
    for node in blockchain.yield_nodes():
        if node.identifier != primary_validator.identifier:
            nodes.append(node)

    nodes.append(primary_validator)
    return nodes
