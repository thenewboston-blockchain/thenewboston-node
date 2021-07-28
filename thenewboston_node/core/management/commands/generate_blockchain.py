import os
import os.path

from django.core.management import BaseCommand, CommandError

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.utils.blockchain import generate_blockchain


class Command(BaseCommand):
    help = 'Generate blockchain of random transactions'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('size', type=int, help='Number of blocks to generate')
        parser.add_argument(
            '--path', help='Blockchain base directory (if not specified then memory blockchain is used)'
        )
        parser.add_argument('--do-not-validate', action='store_true')
        parser.add_argument('--force', '-f', action='store_true', help='Replace blockchain even if it exists')

    def handle(self, size, path, do_not_validate, force, *args, **options):
        if path:
            base_directory = os.path.abspath(path)
            blockchain = FileBlockchain(base_directory=base_directory)
            if not blockchain.is_empty():
                if force:
                    blockchain.clear()
                else:
                    raise CommandError(f'There is non-empty blockchain at {base_directory}')
        else:
            blockchain = MemoryBlockchain()

        validate = not do_not_validate
        generate_blockchain(blockchain, size, validate=validate, signing_key=get_node_signing_key())
