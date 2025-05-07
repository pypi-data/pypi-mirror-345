__all__ = (
    'QUOTA_EXCEEDED_ERROR',
    'BMLLError',
    'ConnectivityError',
    'AuthenticationError',
    'LoginError',
    'MarketDataError',
    'RequestTooLarge',
    'QuotaReachedError',
)


QUOTA_EXCEEDED_ERROR = 'Limit Exceeded'


class BMLLError(Exception):
    pass


class ConnectivityError(BMLLError):
    """The user was unable to reach the BMLL services"""
    pass


class AuthenticationError(BMLLError):
    """The service was unable to authenticate."""
    pass


class LoginError(BMLLError):
    """An error has occurred when attempting to login to the BMLL Services."""
    pass


class MarketDataError(BMLLError):
    """Failed to retrieve market data."""
    pass


class RequestTooLarge(BMLLError):
    """Request content length is too large, the size of the query should be reduced."""


class QuotaReachedError(BMLLError):
    """User has reached their quota and got a 429 status code."""
