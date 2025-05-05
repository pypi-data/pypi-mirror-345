"""Exceptions for the Signal Messenger Python API."""

from typing import Any, Dict, Optional


class SignalAPIError(Exception):
    """Base exception for Signal API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            status_code: The HTTP status code.
            response: The response body.
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class SignalConnectionError(SignalAPIError):
    """Exception raised when there is a connection error."""

    pass


class SignalTimeoutError(SignalAPIError):
    """Exception raised when a request times out."""

    pass


class SignalAuthenticationError(SignalAPIError):
    """Exception raised when there is an authentication error."""

    pass


class SignalNotFoundError(SignalAPIError):
    """Exception raised when a resource is not found."""

    pass


class SignalBadRequestError(SignalAPIError):
    """Exception raised when a request is malformed."""

    pass


class SignalServerError(SignalAPIError):
    """Exception raised when there is a server error."""

    pass
