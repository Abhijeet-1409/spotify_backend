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
async def handle_auth_callback(
        user_data: Annotated[UserIn, Body()],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
    ) -> JSONResponse:

    content: dict = await auth_service.authCallback(user_data=user_data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=content,
    )