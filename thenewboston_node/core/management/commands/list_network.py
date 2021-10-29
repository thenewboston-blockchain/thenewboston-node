import logging
import sys

from django.core.management.base import BaseCommand

from tabulate import tabulate

from thenewboston_node.business_logic.blockchain.api_blockchain import APIBlockchain
from thenewboston_node.core.clients.node import NodeClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Display list of PV, CVs, other online nodes, offline nodes.'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('network_address')

    @staticmethod
    def find_primary_validator(initial_network_address):
        client = NodeClient.get_instance()
        network_addresses = [initial_network_address]
        for _ in range(10):
            primary_validator = None
            for network_address in network_addresses:
                logger.info('Trying %s to find primary validator', network_address)
                primary_validator = client.get_primary_validator(network_address)
                if not primary_validator:
                    continue

                if network_address in primary_validator['network_addresses']:
                    logger.info('Primary validator is %s', primary_validator)
                    return primary_validator

                break

            if not primary_validator:
                break

            network_addresses = primary_validator['network_addresses']

        return None

    def get_pv_network_address(self, initial_network_address):
        primary_validator = self.find_primary_validator(initial_network_address)
        if not primary_validator:
            logger.warning('Could not find node with Primary Validator role.')
            return None

        node_client = NodeClient.get_instance()
        for pv_network_address in primary_validator['network_addresses']:
            if node_client.is_node_online((pv_network_address,), expected_identifier=primary_validator['identifier']):
                return pv_network_address

        logger.warning('Primary validator %s is offline', primary_validator)
        return None

    def handle(self, *args, **options):
        pv_network_address = self.get_pv_network_address(options['network_address'])
        if not pv_network_address:
            logger.warning('Could not find an online primary validator')
            sys.exit(1)

        api_blockchain = APIBlockchain(network_address=pv_network_address)

        node_client = NodeClient.get_instance()
        nodes = []
        for node in api_blockchain.yield_nodes():
            node_identifier = node.identifier

            node.is_online = node_client.is_node_online(node.network_addresses, expected_identifier=node_identifier)
            node.last_block_number = api_blockchain.get_last_block_number()
            node.role = api_blockchain.get_node_role(node_identifier)

            nodes.append(node)

        sorted_nodes = sorted(nodes, key=lambda node_: (not node_.is_online, node_.role.value))
        headers = ('identifier', 'role', 'network_addresses', 'last_block_number', 'is_online')
        printable_nodes = [[getattr(node, header) for header in headers] for node in sorted_nodes]
        print(tabulate(printable_nodes, headers=headers, tablefmt='simple'))
