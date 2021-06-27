import json
import logging
import os
import os.path
from contextlib import closing
from urllib.request import urlopen

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import BlockchainState
from thenewboston_node.business_logic.storages.file_system import FileSystemStorage
from thenewboston_node.core.utils.misc import is_valid_url

logger = logging.getLogger()


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


def make_blockchain_state_from_account_root_file(source, path=None):
    message = f'Reading account root file from {source}'
    logger.info(message)
    account_root_file = read_source(source)
    logger.info('DONE: %s', message)

    logger.info('Converting')
    blockchain_state = BlockchainState.from_account_root_file(account_root_file)
    logger.info('DONE: Converting')

    logger.info('Writing result')
    write_destination(blockchain_state, path=path)
    logger.info('DONE: Writing result')
