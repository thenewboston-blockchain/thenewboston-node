from thenewboston_node.business_logic.exceptions import BlockchainLockedError, BlockchainUnlockedError

LOCKED_EXCEPTION = BlockchainLockedError('Blockchain locked. Probably it is being modified by another process')
EXPECTED_LOCK_EXCEPTION = BlockchainUnlockedError('Blockchain was expected to be locked')


class FileBlockchainBaseMixin:

    def get_base_directory(self) -> str:
        raise NotImplementedError('Must be implemented in child class')

    def get_block_number_digits_count(self) -> int:
        raise NotImplementedError('Must be implemented in child class')

    def get_block_chunk_size(self) -> int:
        raise NotImplementedError('Must be implemented in child class')
