import uuid

from django.db import models

from thenewboston_node.blockchain.managers import PendingBlockManager


class PendingBlock(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    block = models.JSONField()
    block_number = models.IntegerField()
    block_hash = models.CharField(max_length=128)

    objects = PendingBlockManager()

    class Meta:
        unique_together = ['block_number', 'block_hash']
        ordering = ['-block_number']

    def __str__(self):
        return f'block_number={self.block_number}, hash={self.block_hash}'
