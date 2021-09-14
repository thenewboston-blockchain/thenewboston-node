import logging
import os.path
from urllib.parse import urlparse

from django.core.management import BaseCommand, CommandError

from thenewboston_node.business_logic.storages.file_system import get_compressor_from_location
from thenewboston_node.core.clients.node import NodeClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Download latest blockchain state'  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('node_address')
        parser.add_argument('--target', '-t', default='./')

    def handle(self, *args, **options):
        node_address = options['node_address']
        client = NodeClient.get_instance()

        logger.info('Reading latest blockchain state binary from %s', node_address)
        result = client.get_latest_blockchain_state_binary_by_network_address(node_address)
        if result is None:
            raise CommandError(f'Could not get latest blockchain state binary from {node_address}')

        data, url = result

        filename = os.path.basename(urlparse(url).path)
        target = options['target']
        if os.path.isdir(target):
            file_path = os.path.join(target, filename)
        else:
            compressor = get_compressor_from_location(filename)
            file_path = target.format(compressor=('.' + compressor) if compressor else '')

        logger.info('Writing latest blockchain state binary to %s', file_path)
        with open(file_path, 'wb') as fo:
            fo.write(data)
