from django.core.management import BaseCommand

from thenewboston_node.business_logic.docs.impl import main


class Command(BaseCommand):
    help = 'Generate blockchain structure documentation'  # noqa: A003

    def handle(self, *args, **options):
        main()
