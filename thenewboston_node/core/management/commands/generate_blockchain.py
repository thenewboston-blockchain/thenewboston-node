import os
import os.path

from django.core.management import BaseCommand, CommandError

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.utils.blockchain import generate_blockchain


class Command(BaseCommand):
    help = 'Generate blockchain of random transactions'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('size', type=int, help='Number of blocks to generate')
        parser.add_argument(
            '--path', help='Blockchain base directory (if not specified then memory blockchain is used)'
        )
        parser.add_argument('--do-not-validate', action='store_true')

    def handle(self, size, path=None, do_not_validate=False, *args, **options):
        validate = not do_not_validate
        if path:
            os.makedirs(path, exist_ok=True)

            if os.listdir(path):
                raise CommandError(f'Path {path} contains files')

            blockchain = FileBlockchain(base_directory=os.path.abspath(path))
        else:
            blockchain = MemoryBlockchain()

        generate_blockchain(blockchain, size, validate=validate)
