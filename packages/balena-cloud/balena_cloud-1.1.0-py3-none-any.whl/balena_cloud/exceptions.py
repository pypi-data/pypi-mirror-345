"""Asynchronous Python client for Balena Cloud."""


class BalenaCloudError(Exception):
    """Base class for Balena Cloud exceptions."""


class BalenaCloudAuthenticationError(BalenaCloudError):
    """Exception raised when the API key is invalid."""


class BalenaCloudConflictError(BalenaCloudError):
    """Exception raised when a conflict occurs."""

    def __init__(self, message: str, code: int) -> None:
        """Initialize the exception."""
        super().__init__(f"{message} (code: {code})")


class BalenaCloudConnectionError(BalenaCloudError):
    """Exception raised when a connection error occurs."""


class BalenaCloudParameterValidationError(BalenaCloudError):
    """Exception raised when a parameter is missing or invalid."""


class BalenaCloudResourceNotFoundError(BalenaCloudError):
    """Exception raised when a resource is not found."""
