from bson import ObjectId

from typing import Optional

from datetime import datetime, timezone

from pydantic import BaseModel,HttpUrl,Field,field_serializer

class SongDB(BaseModel):
    id: ObjectId = Field(default_factory=lambda: ObjectId(),title="Id",description="Song's Id",alias="_id")
    title: str = Field(title="Title",description="Song's title")
    artist: str = Field(title="Artist",description="Artist's Name")
    image_url: Optional[HttpUrl] = Field(default=None,title="Image Url",description="Song's cover image")
    audio_url: Optional[HttpUrl] = Field(default=None,title="Audio Url",description="Song's actual audio")
    duration: int = Field(title="Duration",description="Song's duration")
    created_at: datetime = Field(
                                    default_factory=lambda: datetime.now(timezone.utc),
                                    title="Created At",
                                    description="Timestamp when the song was created"
                                )
    album_id: Optional[ObjectId] = Field(
                                            default=None,
                                            title="Album Id",
                                            description="Reference to album which song belongs to"
                                        )

    @field_serializer('image_url')
    def serialize_image_url(self, value: Optional[HttpUrl], _info) -> str:
        if not value:
            return None
        return str(value)

    @field_serializer('audio_url')
    def serialize_audio_url(self, value: Optional[HttpUrl], _info) -> str:
        if not value:
            return None
        return str(value)

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
    }
