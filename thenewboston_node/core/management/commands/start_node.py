import logging

from django.conf import settings
from django.core.management import BaseCommand

import stun

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import (
    Block, NodeDeclarationSignedChangeRequest, NodeDeclarationSignedChangeRequestMessage,
    PrimaryValidatorScheduleSignedChangeRequest
)
from thenewboston_node.business_logic.node import derive_public_key, get_node_signing_key
from thenewboston_node.business_logic.utils.blockchain_state import make_blockchain_state_from_account_root_file

logger = logging.getLogger(__name__)


def initialize_blockchain(source, failover_source=None):
    try:
        make_blockchain_state_from_account_root_file(source)
    except Exception:
        logger.exception('Could not get initial blockchain from %s (failing over to %s)', source, failover_source)
        if failover_source:
            make_blockchain_state_from_account_root_file(failover_source)


def get_network_addresses():
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


def self_declare_node(blockchain, network_addresses):
    signing_key = get_node_signing_key()
    identifier = derive_public_key(signing_key)
    logger.info('Self declaring with %s', identifier)
    message = NodeDeclarationSignedChangeRequestMessage.create(
        identifier=identifier,
        network_addresses=network_addresses,
        fee_amount=settings.NODE_FEE_AMOUNT,
        fee_account=settings.NODE_FEE_ACCOUNT,
    )
    request = NodeDeclarationSignedChangeRequest.create_from_signed_change_request_message(message, signing_key)
    # TODO(dmu) CRITICAL: Lock blockchain here
    block = Block.create_from_signed_change_request(blockchain, request, signing_key)
    blockchain.add_block(block)
    # TODO(dmu) CRITICAL: Release blockchain lock here


def self_declare_as_primary_validator(blockchain: BlockchainBase, begin_block_number):
    signing_key = get_node_signing_key()
    end_block_number = begin_block_number + settings.SCHEDULE_DEFAULT_LENGTH_IN_BLOCKS - 1
    request = PrimaryValidatorScheduleSignedChangeRequest.create(begin_block_number, end_block_number, signing_key)
    block = Block.create_from_signed_change_request(blockchain, request, signing_key)
    blockchain.add_block(block)


class Command(BaseCommand):
    help = 'Start node'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('blockchain_genesis_state_source')
        parser.add_argument('--failover-blockchain-genesis-state-source')
        parser.add_argument('--replace-blockchain', action='store_true')

    def handle(self, *args, **options):
        blockchain = BlockchainBase.get_instance()
        if not blockchain.is_empty() and options['replace_blockchain']:
            blockchain.clear()

        if blockchain.is_empty():
            blockchain_genesis_state_source = options['blockchain_genesis_state_source']
            logger.info('Empty blockchain detected: initializing with %s', blockchain_genesis_state_source)
            initialize_blockchain(
                blockchain_genesis_state_source, failover_source=options['failover_blockchain_genesis_state_source']
            )

        if not blockchain.has_nodes():
            logger.info(
                'No nodes are detected, turns out we are the first node on the blockchain '
                '(will register ourselves as node and primary validator)'
            )
            network_addresses = get_network_addresses()
            if not network_addresses:
                logger.info('Network addresses are neither configured explicitly nor auto detected')
                return

            # TODO(dmu) LOW: For a valid blockchain without blocks ``begin_block_number`` should always be equal to 0.
            #                Maybe we should investigate this edge case more, or just keep this forward compatible
            #                implementation with ``blockchain.get_next_block_number()``
            begin_block_number = blockchain.get_next_block_number()
            self_declare_node(blockchain, network_addresses)
            self_declare_as_primary_validator(blockchain, begin_block_number)
            return

        raise NotImplementedError('Blockchain has nodes workflow is not implemented yet')
