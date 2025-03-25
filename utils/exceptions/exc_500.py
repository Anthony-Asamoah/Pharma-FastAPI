"""
The HTTP 500 Internal Server Error response status code indicates that the server encountered
an unexpected condition that prevented it from fulfilling the request.
"""
from fastapi import HTTPException, status


async def http_500_exc_internal_server_error() -> Exception:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Something went wrong! Kindly try again or contact support.",
    )
