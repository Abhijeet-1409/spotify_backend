from bson import ObjectId

from datetime import datetime

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator, field_serializer

from app.models.song import SongDB

class SongIn(BaseModel):
    title: str = Field(title="Title",description="Song's title")
    artist: str = Field(title="Artist",description="Artist's Name")
    duration: int = Field(title="Duration",description="Song's duration")
    album_id: Optional[str] = Field(
                                    default=None,
                                    title="Album Id",
                                    description="Reference to album which song belongs to"
                                )


    @field_validator('album_id', mode="before")
    @classmethod
    def validate_album_id(cls, value: str | None) -> str | None:
        if not value :
            return None
        if not ObjectId.is_valid(value):
            raise ValueError("album_id is not a valid ObjectId")
        return value


    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        album_id = data['album_id']
        data['album_id'] = ObjectId(album_id) if album_id else None
        return data


class SongOut(SongDB):

    image_url: HttpUrl = Field(title="Image Url",description="Song's cover image",alias="imageUrl")
    audio_url: HttpUrl = Field(title="Audio Url",description="Song's actual audio",alias="audioUrl")
    created_at: datetime = Field(title="Created At",description="Timestamp when the song was created",alias="createdAt")
    album_id: Optional[ObjectId] = Field(title="Album Id",description="Reference to album which song belongs to",alias="albumId")

    @field_serializer('id')
    def serialize_id(self, value: ObjectId, _info) -> str:
        return str(value)

    @field_serializer('album_id')
    def serialize_album_id(self, value: Optional[ObjectId], _info) -> str:
        return str(value) if value else None

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat()
