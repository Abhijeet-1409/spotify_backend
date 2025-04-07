from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, File

from app.core.config import Settings
from app.schemas.song import SongIn, SongOut
from app.services.admin import AdminService
from app.dependencies.dependencies import (
    get_settings,
    extract_song_data,
    custom_file_validation,
    get_admin_service
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

settings: Settings = get_settings()
MAX_FILE_SIZE_MB: int = settings.MAX_FILE_SIZE_MB

song_image_validation = custom_file_validation(MAX_FILE_SIZE_MB, "Image")
song_audio_validation = custom_file_validation(MAX_FILE_SIZE_MB, "Audio")


@router.post("/songs")
async def handle_create_song(
        song_data: Annotated[SongIn, Depends(extract_song_data)],
        image_file: Annotated[UploadFile, File()],
        audio_file: Annotated[UploadFile, File()],
        admin_service: Annotated[AdminService, Depends(get_admin_service)],
        background_tasks: BackgroundTasks
    ) -> SongOut :

    validated_image_file: UploadFile = await song_image_validation(image_file)
    validated_audio_file: UploadFile = await song_audio_validation(audio_file)

    song_out: SongOut = await admin_service.create_song(
        song_data=song_data,
        image_file=validated_image_file,
        audio_file=validated_audio_file,
        background_tasks=background_tasks
    )

    return song_out