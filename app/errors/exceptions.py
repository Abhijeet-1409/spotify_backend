from typing import Annotated, Any, Dict, Optional
from fastapi import HTTPException, status


class InternalServerError(HTTPException):
    """Exception class for representing internal server errors."""

    def __init__(
        self,
        detail: Annotated[Any, "Error message describing the internal server error"] = "Internal Server Error",
        headers: Annotated[Optional[Dict[str, str]], "Optional headers for the response"] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers
        )
