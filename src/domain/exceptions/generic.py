"""
Generic Exceptions
"""


class BaseDomainException(Exception):
    """
    Base domain exception
    """

    def __init__(self, message: str, *args):
        self.message = message
        super().__init__(message, *args)


class NotFoundException(BaseDomainException):
    """
    Exception for not found object existence
    """


class DuplicateException(BaseDomainException):
    """
    Exception for duplicate object existence
    """


class SecurityError(BaseDomainException):
    """
    Exception for security error
    """


class BlobException(BaseDomainException):
    """
    Exception for blob storage errors
    """

    def __init__(self, message: str, code: int = 500, detail: any = None, *args):
        self.code = code
        self.detail = detail
        super().__init__(message, *args)
