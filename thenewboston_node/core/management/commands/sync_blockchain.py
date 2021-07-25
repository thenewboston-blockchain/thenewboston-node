from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.utils.network import get_ranked_nodes


class Command(BaseCommand):
    help = 'Sync blockchain'  # noqa: A003

    def handle(self, *args, **options):
        blockchain = BlockchainBase.get_instance()
        for node in get_ranked_nodes(blockchain):
            print(node)

        raise NotImplementedError
