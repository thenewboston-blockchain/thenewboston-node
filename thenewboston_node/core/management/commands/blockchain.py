from pprint import pformat

from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase

GET_BLOCK = 'get-block'
GET_BLOCKS = 'get-blocks'
GET_BLOCKCHAIN_STATE = 'get-blockchain-state'

FILE_INTERFACE = 'file'
API_INTERFACE = 'api'


class Command(BaseCommand):
    help = 'Blockchain managements commands'  # noqa: A003

    def __init__(self, *args, **kwargs):
        self.blockchain = None
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            '--interface',
            type=str,
            choices=[FILE_INTERFACE, API_INTERFACE],
            default=FILE_INTERFACE,
            help='Select one of possible blockchain interface'
        )

        subparsers = parser.add_subparsers(title='Blockchain management commands', dest='command', required=True)

        get_block_parser = subparsers.add_parser(GET_BLOCK, help='Print block JSON by block number')
        get_block_parser.add_argument('block_number', nargs='?', type=int)

        get_blocks_parser = subparsers.add_parser(GET_BLOCKS, help='Print range of block JSONs by block numbers')
        get_blocks_parser.add_argument('start_block', nargs='?', type=int)
        get_blocks_parser.add_argument('end_block', nargs='?', type=int)

        get_blockchain_state_parser = subparsers.add_parser(
            GET_BLOCKCHAIN_STATE, help='Print blockchain state by block number'
        )
        get_blockchain_state_parser.add_argument('block_number', nargs='?', type=int)

    def handle(self, interface, *args, **options):
        interfaces = {
            FILE_INTERFACE: self.init_file_blockchain,
            API_INTERFACE: self.init_api_blockchain,
        }

        init_interface = interfaces[interface]
        init_interface()
        assert self.blockchain is not None

        commands = {
            GET_BLOCK: self.print_block,
            GET_BLOCKS: self.print_blocks,
            GET_BLOCKCHAIN_STATE: self.print_blockchain_state,
        }
        exec_command = commands[options['command']]
        exec_command(*args, **options)

    def init_file_blockchain(self):
        self.blockchain = BlockchainBase.get_instance()

    def init_api_blockchain(self):
        raise NotImplementedError('Must be implemented soon')

    def print_block(self, block_number, *args, **options):
        block = self.blockchain.get_block_by_number(block_number)
        if block is None:
            return
        self._print_blockchain_model(block)

    def print_blocks(self, start_block, end_block, *args, **options):
        if start_block > end_block:
            self.stdout.write(self.style.ERROR('End block argument should be equal or more than start block.'))
            return

        for block in self.blockchain.yield_blocks_from(start_block):
            self._print_blockchain_model(block)

    def print_blockchain_state(self, block_number, *args, **options):
        state = self.blockchain.get_blockchain_state_by_block_number(block_number)
        self._print_blockchain_model(state)

    def _print_blockchain_model(self, blockchain_model):
        serialized_model = blockchain_model.serialize_to_dict()
        self.stdout.write(pformat(serialized_model))
