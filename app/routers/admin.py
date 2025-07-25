from typing import Annotated

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, File, Path, status

from clerk_backend_api.models.user import User as ClerkUser

from app.core.config import Settings
from app.schemas.song import SongIn, SongOut
from app.schemas.album import AlbumIn, AlbumOut
from app.services.admin import AdminService
from app.dependencies.dependencies import (
    get_settings,
    require_admin,
    get_admin_service,
    extract_song_data,
    extract_album_data,
    custom_file_validation,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)]
)

settings: Settings = get_settings()
MAX_FILE_SIZE_MB: int = settings.MAX_FILE_SIZE_MB

song_image_validation = custom_file_validation(MAX_FILE_SIZE_MB, "Image")
song_audio_validation = custom_file_validation(MAX_FILE_SIZE_MB, "Audio")


@router.get("/check")
async def check_admin(admin: Annotated[ClerkUser, Depends(require_admin)]):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"admin": True}
    )


@router.post("/songs")
async def create_song_with_files(
        image_file: Annotated[UploadFile, File(alias="imageFile")],
        audio_file: Annotated[UploadFile, File(alias="audioFile")],
        song_data: Annotated[SongIn, Depends(extract_song_data)],
        admin_service: Annotated[AdminService, Depends(get_admin_service)],
        background_tasks: BackgroundTasks
    ) -> SongOut:

    validated_image_file: UploadFile = await song_image_validation(image_file)
    validated_audio_file: UploadFile = await song_audio_validation(audio_file)

    song_out: SongOut = await admin_service.create_song(
        song_data=song_data,
        image_file=validated_image_file,
        audio_file=validated_audio_file,
        background_tasks=background_tasks
    )

    return song_out


@router.delete("/songs/{id}")
async def delete_song_with_files(
        id: Annotated[str, Path()],
        admin_service: Annotated[AdminService, Depends(get_admin_service)],
        background_tasks: BackgroundTasks,
    ) -> JSONResponse:

    response_data: dict = await admin_service.delete_song(
        song_id=id,
        background_tasks=background_tasks
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data,
    )


@router.post("/albums")
async def create_album_with_files(
        image_file: Annotated[UploadFile, File(alias="imageFile")],
        album_data: Annotated[AlbumIn, Depends(extract_album_data)],
        admin_service: Annotated[AdminService, Depends(get_admin_service)],
        background_tasks: BackgroundTasks
    ) -> AlbumOut:

    validated_image_file: UploadFile = await song_image_validation(image_file)

    album_out: AlbumOut = await admin_service.create_album(
        image_file=validated_image_file,
        album_data=album_data,
        background_tasks=background_tasks
    )

    return album_out


@router.delete("/albums/{id}")
async def delete_albums_with_files(
        id: Annotated[str, Path()],
        admin_service: Annotated[AdminService, Depends(get_admin_service)],
        background_tasks: BackgroundTasks
    ) -> JSONResponse:

    response_data: dict = await admin_service.delete_album(
        album_id=id,
        background_tasks=background_tasks
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data,
    )