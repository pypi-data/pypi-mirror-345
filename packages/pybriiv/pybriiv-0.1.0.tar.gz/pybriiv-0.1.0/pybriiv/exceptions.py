"""Exceptions for the Briiv API."""


class BriivError(Exception):
    """Base exception for Briiv API."""


class BriivCallbackError(BriivError):
    """Exception for callback errors."""


class BriivConnectionError(BriivError):
    """Exception for connection errors."""


class BriivCommandError(BriivError):
    """Exception for command errors."""
