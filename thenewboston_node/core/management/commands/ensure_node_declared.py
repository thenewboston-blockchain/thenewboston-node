import logging

from django.core.management import BaseCommand

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.node import get_node_identifier, get_node_signing_key
from thenewboston_node.business_logic.utils.network import make_own_node
from thenewboston_node.core.clients.node import NodeClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ensure node is declared'  # noqa: A003

    def handle(self, *args, **options):
        stdout = self.stdout

        blockchain = BlockchainBase.get_instance()

        node_identifier = get_node_identifier()
        stdout.write(f'Node identifier: {node_identifier}')
        existing_node = blockchain.get_node_by_identifier(node_identifier, blockchain.get_last_block_number())
        if existing_node is not None:
            stdout.write(f'Node is declared as {existing_node}')

        expected_node = make_own_node()
        stdout.write(f'Expected node declaration: {expected_node}')
        if existing_node == expected_node:
            stdout.write('Node declaration is intact')
            return

        primary_validator = blockchain.get_primary_validator()
        signed_change_request = NodeDeclarationSignedChangeRequest.create_from_node(
            node=expected_node, signing_key=get_node_signing_key()
        )
        stdout.write(f'Sending node declaration: {signed_change_request}')
        NodeClient.get_instance().send_signed_change_request_to_node(primary_validator, signed_change_request)
