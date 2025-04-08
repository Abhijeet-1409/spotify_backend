from typing import List, Annotated

from fastapi import APIRouter, Path, Depends

from app.schemas.album import AlbumOut
from app.services.album import AlbumService
from app.dependencies.dependencies import get_album_service


router = APIRouter(
    prefix="/api/albums",
    tags=["albums"]
)


@router.get("/")
async def get_all_albums(
        album_service: Annotated[AlbumService, Depends(get_album_service)]
    ) -> List[AlbumOut]:

    album_out_list: List[AlbumOut] = await album_service.fetch_all_albums()

    return album_out_list


@router.get("/{id}")
async def get_album_by_id(
        id: Annotated[str, Path()],
        album_service: Annotated[AlbumService, Depends(get_album_service)]
    ) -> AlbumOut:

    album_out: AlbumOut = await album_service.fetch_album_by_id(album_id=id)

    return album_out