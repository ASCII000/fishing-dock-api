"""
Generic Exceptions
"""


class BaseDomainException(Exception):
    """
    Base domain exception
    """

    def __init__(self, message: str, *args):
        self.message = message
        super().__init__(*args)


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
