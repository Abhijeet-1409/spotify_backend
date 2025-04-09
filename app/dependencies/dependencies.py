import os

import asyncio

import cloudinary

from typing import Annotated, Optional, List

from functools import lru_cache

from pydantic import ValidationError

from fastapi import Depends, Form, Request, HTTPException, status, UploadFile

from app.core.config import Settings
from app.db.connection import DatabaseConnection
from app.schemas.song import SongIn
from app.schemas.album import AlbumIn
from app.services.auth import AuthService
from app.services.admin import AdminService
from app.services.album import AlbumService
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

@lru_cache()
def init_clerk_sdk(secret_key: str) -> Clerk:
    return Clerk(bearer_auth=secret_key)

def get_clerk_sdk(settings: Annotated[Settings, Depends(get_settings)]) -> Clerk:
    try :
        return init_clerk_sdk(settings.CLERK_SECRET_KEY)
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

    except HTTPException as http_err :
        raise http_err

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

def extract_song_data(
        title: Annotated[str, Form(title="Title",description="Song's title")],
        artist: Annotated[str, Form(title="Artist",description="Artist's Name")],
        duration: Annotated[int, Form(title="Duration",description="Song's duration")],
        album_id: Annotated[
                    Optional[str],
                    Form(
                        title="Album Id",
                        description="Reference to album which song belongs to"
                    )
                ] = None
    ) -> SongIn :

    try :
        return SongIn(title=title,artist=artist,duration=duration,album_id=album_id)

    except ValidationError as validation_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
             detail=[{"loc": err["loc"], "msg": err["msg"]} for err in validation_err.errors()]
        )

    except Exception as err:
        raise InternalServerError() from err

def get_file_size(file: UploadFile) -> int:
    file.file.seek(0, os.SEEK_END)
    return file.file.tell()

def custom_file_validation(max_size_mb: int, file_type: str):
    allowed_image_formats: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    allowed_audio_formats: List[str] = ["mp3", "wav", "flac", "aac", "ogg"]

    async def validate_file(file: UploadFile) -> UploadFile:
        file_size: int = await asyncio.to_thread(get_file_size,file)
        await file.seek(0)

        errors: List[str] = []

        file_name = file.filename.strip() if file.filename else ""
        file_extension = os.path.splitext(file_name)[-1].lower().strip(".")

        allowed_formats = (
            allowed_image_formats if file_type.lower() == "image" else allowed_audio_formats
        )

        if not file_name or " " in file_name or not file_name[0].isalpha():
            errors.append(f"Invalid file name '{file_name}'. It must not contain spaces and must start with a letter.")

        if file_extension not in allowed_formats:
            errors.append(
                f"Invalid file type '{file_extension}' for {file_type}. Allowed types: {', '.join(allowed_formats)}."
            )

        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            errors.append(f"File '{file_name}' exceeds the size limit of {max_size_mb}MB.")

        if errors:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)

        return file

    return validate_file

def get_admin_service(db_instance: Annotated[DatabaseConnection, Depends(get_database_connection)]) -> AdminService:
    return AdminService(db_instance=db_instance)

def extract_album_data(
        title: Annotated[str, Form(title="Title",description="Album's title")],
        artist: Annotated[str, Form(title="Artist",description="Album's artist")],
        release_year: Annotated[int, Form(title="Release Year",description="Album's release year")],
    ) -> AlbumIn :

    try :
        return AlbumIn(title=title,artist=artist,release_year=release_year)

    except ValidationError as validation_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
             detail=[{"loc": err["loc"], "msg": err["msg"]} for err in validation_err.errors()]
        )

    except Exception as err:
        raise InternalServerError() from err

def get_album_service(db_instance: Annotated[DatabaseConnection, Depends(get_database_connection)]) -> AlbumService:
    return AlbumService(db_instance=db_instance)