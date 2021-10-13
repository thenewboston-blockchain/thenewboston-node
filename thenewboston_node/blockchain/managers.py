from django.db import models

from thenewboston_node.business_logic.models import Block


class PendingBlockManager(models.Manager):

    def get_or_create_for_block(self, block: Block):
        return self.get_or_create(
            block_number=block.message.block_number,
            block_hash=block.hash,
            defaults={'block': block.serialize_to_dict()},
        )
