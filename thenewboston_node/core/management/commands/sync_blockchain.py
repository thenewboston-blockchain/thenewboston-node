import logging

from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.api_blockchain import APIBlockchain
from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.node import get_node_identifier
from thenewboston_node.business_logic.utils.blockchain import sync_minimal_to_file_blockchain
from thenewboston_node.business_logic.utils.network import get_ranked_nodes

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync blockchain'  # noqa: A003

    def handle(self, *args, **options):
        blockchain = BlockchainBase.get_instance()
        assert isinstance(blockchain, FileBlockchain)

        me = get_node_identifier()
        nodes = [node for node in get_ranked_nodes(blockchain) if node.identifier != me]
        if not nodes:
            message = 'Other nodes (to synchronize with) are not detected on the network'
            self.stdout.write(message)
            logger.info(message)
            return

        # TODO(dmu) MEDIUM: Consider an option to synchronize blockchain with all nodes on the network
        #                   in case a chosen node is stale
        for node in nodes:
            for network_address in node.network_addresses:
                source = APIBlockchain(network_address=network_address)
                try:
                    sync_minimal_to_file_blockchain(source, blockchain)
                    message = f'Successfully synchronized blockchain with {network_address}'
                    self.stdout.write(message)
                    logger.info(message)
                    return
                except Exception:
                    logger.warning(
                        'Could not synchronize blockchain with %s at %s',
                        node.identifier,
                        network_address,
                        exc_info=True
                    )
        else:
            logger.error('Could not synchronize blockchain with the network')
