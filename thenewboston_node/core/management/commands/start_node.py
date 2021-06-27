import logging

from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.utils.blockchain_state import make_blockchain_state_from_account_root_file

logger = logging.getLogger(__name__)


def initialize_blockchain(source, failover_source=None):
    try:
        make_blockchain_state_from_account_root_file(source)
    except Exception:
        logger.exception('Could not get initial blockchain from %s (failing over to %s)', source, failover_source)
        if failover_source:
            make_blockchain_state_from_account_root_file(failover_source)


class Command(BaseCommand):
    help = 'Start node'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('blockchain_genesis_state_source')
        parser.add_argument('--failover-blockchain-genesis-state-source')

    def handle(self, *args, **options):
        blockchain = BlockchainBase.get_instance()
        if blockchain.is_empty():
            blockchain_genesis_state_source = options['blockchain_genesis_state_source']
            logger.info('Empty blockchain detected: initializing with %s', blockchain_genesis_state_source)
            initialize_blockchain(
                blockchain_genesis_state_source, failover_source=options['failover_blockchain_genesis_state_source']
            )
