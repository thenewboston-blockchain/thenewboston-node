from .base import BlockchainBase


class MockBlockchain(BlockchainBase):  # pragma: no cover
    """
    A blockchain dummy "implementation" to be mocked in unittests
    """

    def add_account_root_file(self, account_root_file):
        pass
