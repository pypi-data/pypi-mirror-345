# olostep_sdk/request_wrapper.py
import requests

from olostep_sdk.olostep_exceptions import (
    ForbiddenError,
    NotFoundError,
    OlostepError,
    PaymentRequiredError,
    RateLimitExceededError,
    UnauthorizedError,
)


def make_request(method: str, url: str, headers: dict | None = None, **kwargs) -> dict:
    """Unified request wrapper that handles HTTP errors and raises custom exceptions."""
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code

        if status == 401:
            raise UnauthorizedError("Invalid or missing API token.") from e
        elif status == 402:
            raise PaymentRequiredError(
                "Payment required to access this resource."
            ) from e
        elif status == 403:
            raise ForbiddenError("Access forbidden.") from e
        elif status == 404:
            raise NotFoundError("Resource not found.") from e
        elif status == 429:
            raise RateLimitExceededError("Rate limit exceeded.") from e
        else:
            raise OlostepError(f"Unexpected HTTP error ({status})") from e
    except requests.RequestException as e:
        raise OlostepError("Network error or invalid request") from e
