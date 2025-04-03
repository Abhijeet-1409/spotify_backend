import asyncio

import cloudinary

from typing import Annotated

from functools import lru_cache

from fastapi import Depends, Request, HTTPException, status

from app.core.config import Settings
from app.db.connection import DatabaseConnection
from app.services.auth import AuthService
from app.errors.exceptions import InternalServerError

from clerk_backend_api import Clerk
from clerk_backend_api.models.user import User as ClerkUser
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions, RequestState

@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_database_connection(settings: Annotated[Settings, Depends(get_settings)]) -> DatabaseConnection:
    return DatabaseConnection(settings=settings)

def get_auth_service(db_instance: Annotated[DatabaseConnection, Depends(get_database_connection)]) -> AuthService:
    return AuthService(db_instance=db_instance)

def get_clerk_sdk(settings: Annotated[Settings, Depends(get_settings)]) -> Clerk:
    try :
        return Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
    except Exception as err :
        raise InternalServerError() from err

def sync_authenticate_request(request: Request, clerk_sdk: Clerk) -> RequestState:
    return clerk_sdk.authenticate_request(request=request,options=AuthenticateRequestOptions())

async def protect_route(request: Request, clerk_sdk: Annotated[Clerk, Depends(get_clerk_sdk)]) -> ClerkUser:
    try :
        request_state: RequestState = await asyncio.to_thread(sync_authenticate_request,request,clerk_sdk)

        if not request_state.is_signed_in :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized - you must be logged in",
            )

        user_id: str = request_state.payload.get("sub")
        clerk_user: ClerkUser = await clerk_sdk.users.get_async(user_id=user_id)

        return clerk_user

    except Exception as err :
        raise InternalServerError() from err

async def require_admin(settings: Annotated[Settings, Depends(get_settings)], clerk_user: Annotated[ClerkUser, Depends(protect_route)]) -> ClerkUser:
    primary_email_address_id: str | None = clerk_user.primary_email_address_id

    admin_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized - you must be an admin",
    )

    if not primary_email_address_id:
        raise admin_exception

    primary_email_address = next(
        (email.email_address for email in clerk_user.email_addresses if email.id == primary_email_address_id),
        None
    )

    if primary_email_address != settings.ADMIN_EMAIL:
        raise admin_exception

    return clerk_user

def init_cloudinary(settings: Settings) -> None :
    cloudinary.config(
        cloud_name = settings.CLOUDINARY_CLOUD_NAME,
        api_key = settings.CLOUDINARY_API_KEY,
        api_secret = settings.CLOUDINARY_SECRET_KEY,
        secure=True
    )