class InvalidBlockError(Exception):
    pass


class ValidationError(Exception):

    def __init__(self, message):
        super(ValidationError, self).__init__(message)


class InvalidSignatureError(ValidationError):

    def __init__(self, message=None):
        super().__init__(message or 'Signature is invalid')


class InvalidMessageSignatureError(InvalidSignatureError):

    def __init__(self, message=None):
        super().__init__(message or 'Message signature is invalid')
