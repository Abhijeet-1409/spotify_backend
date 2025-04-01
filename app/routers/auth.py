from typing import Annotated

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Body, status

from app.schemas.user import UserIn
from app.services.auth import AuthService
from app.dependencies.dependencies import get_auth_service

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post('/callback')
async def auth_callback_handler(
        auth_request_data: Annotated[UserIn, Body()],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
    ) -> JSONResponse:

    response_data: dict = await auth_service.auth_callback(user_auth_data=auth_request_data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data,
    )