class BaseIterableException(Exception):
    """Base exception for iterable project."""


class InputNotIterableError(BaseIterableException):
    """Raise when an input is not iterable."""


class EmptyIterableError(BaseIterableException):
    """Raise when an iterable is found to be empty."""


class IndexOutOfBoundsError(BaseIterableException):
    """Raise when a provided index is out of bounds."""
