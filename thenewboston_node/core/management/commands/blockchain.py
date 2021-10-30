import json

from django.core.management import BaseCommand, CommandError

from thenewboston_node.business_logic.blockchain.api_blockchain import APIBlockchain
from thenewboston_node.business_logic.blockchain.base import BlockchainBase


class Command(BaseCommand):
    help = 'Blockchain managements commands'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument(
            '--remote', type=str, help='Operate on remote blockchain available at providede network address'
        )

        subparsers = parser.add_subparsers(title='Blockchain management commands', dest='command', required=True)

        get_block_parser = subparsers.add_parser('get-block', help='Print block JSON by block number')
        get_block_parser.add_argument('block_number', type=int)

        get_blocks_parser = subparsers.add_parser('get-blocks', help='Print range of block JSONs by block numbers')
        get_blocks_parser.add_argument('start_block_number', type=int)
        get_blocks_parser.add_argument('end_block_number', type=int)

        get_blockchain_state_parser = subparsers.add_parser(
            'get-blockchain-state', help='Print blockchain state by block number'
        )
        get_blockchain_state_parser.add_argument('--block-number', type=int)

    def handle(self, remote, command, *args, **options):
        if remote:
            blockchain = APIBlockchain(network_address=remote)
        else:
            blockchain = BlockchainBase.get_instance()

        command_callable = getattr(self, command.replace('-', '_'))
        command_callable(blockchain, *args, **options)

    def get_block(self, blockchain, block_number, *args, **options):
        block = blockchain.get_block_by_number(block_number)
        if block is None:
            self.write(f'Block number {block_number} was not found in the blockchain')
            return

        self._write_blockchain_object(block)

    def get_blocks(self, blockchain, start_block_number, end_block_number, *args, **options):
        if start_block_number > end_block_number:
            # TODO(dmu) LOW: Consider implementing reversed block traversal in this case instead
            raise CommandError('start_block_number is greater than end_block_number')

        for block in blockchain.yield_blocks_slice(start_block_number, end_block_number):
            self._write_blockchain_object(block)

    def get_blockchain_state(self, blockchain, block_number=None, *args, **options):
        if block_number is None:
            block_number = blockchain.get_last_block_number()

        blockchain_state = blockchain.get_blockchain_state_by_block_number(block_number, inclusive=True)
        self._write_blockchain_object(blockchain_state)

    def _write_blockchain_object(self, blockchain_object):
        object_dict = blockchain_object.serialize_to_dict()
        object_json = json.dumps(object_dict, indent=4)
        self.write(object_json)

    def write(self, *args, **kwargs):
        self.stdout.write(*args, **kwargs)
