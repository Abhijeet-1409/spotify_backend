from typing import Annotated, List

from fastapi import APIRouter, Depends, Path

from clerk_backend_api.models.user import User as ClerkUser

from app.schemas.user import UserOut
from app.schemas.message import MessageOut
from app.services.user import UserService
from app.dependencies.dependencies import (
    protect_route,
    get_user_service
)


router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


@router.get("/")
async def get_all_users(
        user: Annotated[ClerkUser, Depends(protect_route)],
        user_service: Annotated[UserService, Depends(get_user_service)]
    ) -> List[UserOut]:

    current_user_id: str = user.id
    user_out_list: List[UserOut] = await user_service.fetch_all_users(current_user_id)

    return user_out_list


@router.get("/messages/{userId}")
async def get_messages(
        userId: Annotated[str, Path()],
        user: Annotated[ClerkUser, Depends(protect_route)],
        user_service: Annotated[UserService, Depends(get_user_service)]
    ) -> List[MessageOut]:

    current_user_id: str = user.id
    message_out_list: List[MessageOut] = await user_service.fetch_messages(current_user_id,userId)

    return message_out_list