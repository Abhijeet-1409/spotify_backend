from typing import List, Optional

from bson import ObjectId

from datetime import datetime

from app.models.album import AlbumDB

from pydantic import BaseModel, Field, HttpUrl, field_serializer

class AlbumIn(BaseModel):
    title: str = Field(title="Title",description="Album's title")
    artist: str = Field(title="Artist",description="Album's artist")
    release_year: int = Field(title="Release Year",description="Album's release year")


class AlbumOut(AlbumDB):

    image_url: HttpUrl = Field(title="Image Url",description="Album's cover image",alias="imageUrl")
    release_year: int = Field(title="Release Year",description="Album's release year",alias="releaseYear")
    created_at: datetime = Field(title="Created At",description="Timestamp when the album was created",alias="createdAt")

    @field_serializer('id')
    def serialize_id(self, value: ObjectId, _info) -> str:
        return str(value)

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat()

    @field_serializer('songs')
    def serialize_songs(self, value: List[ObjectId], _info) -> List[str]:
        return [str(id) for id in value] if value else []
