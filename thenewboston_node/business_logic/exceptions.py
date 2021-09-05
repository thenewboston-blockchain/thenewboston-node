class BlockchainError(Exception):
    pass


class InvalidBlockError(BlockchainError):
    pass


class ValidationError(BlockchainError):

    def __init__(self, message):
        super(ValidationError, self).__init__(message)


class InvalidSignatureError(ValidationError):

    def __init__(self, message=None):
        super().__init__(message or 'Signature is invalid')


class InvalidMessageSignatureError(InvalidSignatureError):

    def __init__(self, message=None):
        super().__init__(message or 'Message signature is invalid')


class ChangeRequestError(BlockchainError):
    pass


class CoinTransferRequestError(ChangeRequestError):
    pass


class BlockchainLockedError(BlockchainError):
    pass


class BlockchainUnlockedError(BlockchainError):
    pass


class StorageError(Exception):
    pass


class FinalizedFileWriteError(StorageError):
    pass


class InvalidBlockchainError(BlockchainError):
    pass
