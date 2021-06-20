import json
import os
import os.path
from contextlib import closing
from urllib.request import urlopen

from django_tqdm import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import AccountState, BlockchainState
from thenewboston_node.business_logic.storages.file_system import FileSystemStorage
from thenewboston_node.core.utils.misc import is_valid_url


def read_source(source):
    if is_valid_url(source):
        fp = urlopen(source)
    else:
        fp = open(source)

    with closing(fp) as fp:
        return json.load(fp)


def write_default_blockchain(blockchain_state):
    blockchain = BlockchainBase.get_instance()
    blockchain.add_blockchain_state(blockchain_state)


def write_to_file(blockchain_state, path):
    directory, filename = os.path.split(path)
    storage = FileSystemStorage(directory)
    storage.save(filename, blockchain_state.to_messagepack(), is_final=True)


def write_destination(blockchain_state, path=None):
    if path:
        write_to_file(blockchain_state, path)
    else:
        write_default_blockchain(blockchain_state)


class Command(BaseCommand):
    help = 'Convert alpha format account root file to blockchain genesis state'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('source')
        parser.add_argument('--destination-path')

    def handle(self, source, *args, **options):
        self.info(f'Reading account root file from {source}', ending='')
        account_root_file = read_source(source)
        self.info(': DONE')

        self.info('Creating account states', ending='')
        account_states = {}
        for account_number, content in self.tqdm(account_root_file.items(), desc='Creating account states'):
            account_states[account_number] = AccountState(
                balance=content['balance'], balance_lock=content.get('balance_lock')
            )
        self.info(': DONE')

        self.info('Writing result', ending='')
        write_destination(BlockchainState(account_states=account_states), path=options.get('destination_path'))
        self.info(': DONE')
