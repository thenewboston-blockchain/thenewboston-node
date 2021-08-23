import logging
from enum import Enum, unique
from urllib.parse import urlparse

from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain.blockchain_states import (
    get_blockchain_state_file_path_meta
)
from thenewboston_node.business_logic.utils.blockchain_state import (
    add_blockchain_state_from_account_root_file, add_blockchain_state_from_blockchain_state
)
from thenewboston_node.core.utils.misc import humanize_snake_case

logger = logging.getLogger(__name__)


@unique
class SourceType(Enum):
    ACCOUNT_ROOT_FILE = 1
    BLOCKCHAIN_STATE = 2


SOURCE_TYPE_MAKE_BLOCKCHAIN_STATE_MAP = {
    SourceType.ACCOUNT_ROOT_FILE: add_blockchain_state_from_account_root_file,
    SourceType.BLOCKCHAIN_STATE: add_blockchain_state_from_blockchain_state,
}


def guess_source_type(source):
    types = []

    result = urlparse(source)
    meta = get_blockchain_state_file_path_meta(result.path)
    if meta is not None:
        types.append(SourceType.BLOCKCHAIN_STATE)

    if result.path.endswith('.json'):
        types.append(SourceType.ACCOUNT_ROOT_FILE)
    else:
        types.append(SourceType.BLOCKCHAIN_STATE)

    for item in SourceType:
        if item not in types:
            types.append(item)

    return types


def add_blockchain_state_from_sources(blockchain, sources):
    for source in sources:
        logger.info('Adding blockchain state from %s', source)
        for source_type in guess_source_type(source):
            logger.info('Trying source type: %s', humanize_snake_case(source_type.name.lower(), False))
            add_function = SOURCE_TYPE_MAKE_BLOCKCHAIN_STATE_MAP[source_type]
            try:
                add_function(blockchain, source)
                return True
            except Exception:
                logger.warning('%s does not match %s source type or unavailable', source, source_type, exc_info=True)

    return False


class Command(BaseCommand):
    help = 'Initialize blockchain'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('sources', nargs='+', help='file paths or/and URLs to serialized blockchain state or URL')
        parser.add_argument('--force', '-f', action='store_true', help='Replace blockchain even if it exists')

    def handle(self, *args, **options):
        blockchain = BlockchainBase.get_instance()
        if not blockchain.is_empty() and options['force']:
            logger.info('Clearing existing blockchain')
            blockchain.clear()

        if not blockchain.is_empty():
            logger.info('Blockchain is already initialized')
            return

        sources = options['sources']
        has_added = add_blockchain_state_from_sources(blockchain, sources)
        if not has_added:
            logger.error('Was unable to get blockchain source from %s', sources)
