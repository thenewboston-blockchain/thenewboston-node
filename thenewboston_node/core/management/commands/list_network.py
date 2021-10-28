import logging
import sys

from django.core.management.base import BaseCommand

from tabulate import tabulate

from thenewboston_node.business_logic.blockchain.api_blockchain import APIBlockchain
from thenewboston_node.business_logic.enums import NodeRole
from thenewboston_node.core.clients.node import NodeClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Display list of PV, CVs, other online nodes, offline nodes.'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument(
            'network_addresses',
            nargs='?',
            default='http://127.0.0.1:8000/',
            help='Node network address. Default: http://127.0.0.1:8000/'
        )

    def handle(self, *args, **options):
        api_blockchain = APIBlockchain(network_address=options['network_addresses'])
        pv_network_address = None
        for node in api_blockchain.yield_nodes():
            if api_blockchain.get_node_role(node.identifier) == NodeRole.PRIMARY_VALIDATOR:
                for network_address in node.network_addresses:
                    is_online = NodeClient.get_instance().is_node_online(network_address, node.identifier)
                    if is_online:
                        pv_network_address = network_address
                        break
            if pv_network_address is not None:
                break
        if pv_network_address is None:
            logger.warning('Could not find node with Primary Validator role.')
            sys.exit()

        api_blockchain_pv = APIBlockchain(network_address=pv_network_address)

        nodes = []
        for node in api_blockchain_pv.yield_nodes():
            _node = node.serialize_to_dict()
            _node['last_block_number'] = api_blockchain_pv.get_last_block_number()
            _node['is_online'] = NodeClient.get_instance().is_node_online(node.network_addresses[0], node.identifier)
            _node['role'] = api_blockchain_pv.get_node_role(node.identifier)
            nodes.append(_node)

        filtered_nodes = []
        for role in [NodeRole.PRIMARY_VALIDATOR, NodeRole.CONFIRMATION_VALIDATOR, NodeRole.REGULAR_NODE]:
            filtered_nodes.extend(list(filter(lambda r: r['role'] == role.name and r['is_online'] is True, nodes)))
        filtered_nodes.extend(list(filter(lambda r: r['is_online'] is False, nodes)))

        print(tabulate(filtered_nodes, headers='keys', tablefmt='simple'))
