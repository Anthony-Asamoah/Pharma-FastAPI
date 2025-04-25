"""
Raises an HTTPException with status code 500 (Internal Server Error).

Indicates that the server encountered an unexpected condition that prevented
it from fulfilling the request. This is typically used for unhandled exceptions
or unknown server-side issues.

Returns:
    HTTPException: FastAPI exception with status code 500 and a generic error message.
"""

from fastapi import HTTPException, status


async def http_500_exc_internal_server_error() -> Exception:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Something went wrong! Kindly try again or contact support.",
    )
