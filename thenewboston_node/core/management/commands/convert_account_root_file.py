from django.core.management import BaseCommand

from thenewboston_node.business_logic.utils.blockchain_state import make_blockchain_state_from_account_root_file


class Command(BaseCommand):
    help = 'Convert alpha format account root file to blockchain genesis state'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('source')
        parser.add_argument('--destination-path')

    def handle(self, source, destination_path=None, *args, **options):
        make_blockchain_state_from_account_root_file(source, path=destination_path)
