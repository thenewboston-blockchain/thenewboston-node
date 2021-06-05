from .base import BlockchainBase


class MockBlockchain(BlockchainBase):  # pragma: no cover
    """
    A blockchain dummy "implementation" to be mocked in unittests
    """

    def add_blockchain_state(self, blockchain_state):
        pass

    def validate(self, is_partial_allowed: bool = True):
        pass
