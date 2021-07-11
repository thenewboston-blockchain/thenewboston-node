import logging

from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start node'  # noqa: A003

    def handle(self, *args, **options):
        BlockchainBase.get_instance()
        raise NotImplementedError('Blockchain has nodes workflow is not implemented yet')
