# olostep_sdk/olostep_exceptions.py


class OlostepError(Exception):
    """Base exception for all Olostep-related errors."""


class PaymentRequiredError(OlostepError):
    """Raised when the API returns 402 Payment Required."""


class UnauthorizedError(OlostepError):
    """Raised when the API returns 401 Unauthorized."""


class ForbiddenError(OlostepError):
    """Raised when the API returns 403 Forbidden."""


class NotFoundError(OlostepError):
    """Raised when the API returns 404 Not Found."""


class RateLimitExceededError(OlostepError):
    """Raised when the API returns 429 Too Many Requests."""
