from django.core.management import BaseCommand

from thenewboston_node.core.utils.cryptography import generate_key_pair


class Command(BaseCommand):
    help = 'Generate signing (private) key'  # noqa: A003

    def handle(self, *args, **options):
        self.stdout.write(generate_key_pair().private)
