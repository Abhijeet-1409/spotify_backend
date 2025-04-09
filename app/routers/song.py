from typing import List, Annotated

from fastapi import APIRouter, Depends

from clerk_backend_api.models.user import User as ClerkUser

from app.schemas.song import SongOut
from app.services.song import SongService
from app.dependencies.dependencies import(
    require_admin,
    get_song_service
)


router = APIRouter(
    prefix="/api/songs",
    tags=["songs"]
)


@router.get("/")
async def get_all_songs(
        admin: Annotated[ClerkUser, Depends(require_admin)],
        song_service: Annotated[SongService, Depends(get_song_service)]
    ) -> List[SongOut]:

    song_out_list: List[SongOut] = await song_service.fetch_all_songs()

    return song_out_list


@router.get("/featured")
async def get_featured_songs(song_service: Annotated[SongService, Depends(get_song_service)]) -> List[SongOut]:

    song_out_list: List[SongOut] = await song_service.fetch_featured_songs()

    return song_out_list


@router.get("/made-for-you")
async def get_made_for_you_songs(song_service: Annotated[SongService, Depends(get_song_service)]) -> List[SongOut]:

    song_out_list: List[SongOut] = await song_service.fetch_made_for_you_songs()

    return song_out_list


@router.get("/trending")
async def get_trending_songs(song_service: Annotated[SongService, Depends(get_song_service)]) -> List[SongOut]:

    song_out_list: List[SongOut] = await song_service.fetch_trending_songs()

    return song_out_list