from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase


class Command(BaseCommand):
    help = 'Clear blockchain'  # noqa: A003

    def handle(self, *args, **options):
        BlockchainBase.get_instance().clear()
