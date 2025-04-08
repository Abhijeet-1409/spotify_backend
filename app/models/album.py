from bson import ObjectId

from typing import List, Optional

from datetime import datetime, timezone

from pydantic import BaseModel, HttpUrl, Field, field_serializer

class AlbumDB(BaseModel) :
    id: ObjectId = Field(default_factory=lambda: ObjectId(),title="Id",description="Album's Id",alias="_id")
    title: str = Field(title="Title",description="Album's title")
    artist: str = Field(title="Artist",description="Album's artist")
    image_url: Optional[HttpUrl] = Field(default=None,title="Image Url",description="Album's cover image")
    release_year: int = Field(title="Release Year",description="Album's release year")
    songs: List[ObjectId] = Field(default=[],title="Songs",description="Album's Song")
    created_at: datetime = Field(
                                    default_factory=lambda: datetime.now(timezone.utc),
                                    title="Created At",
                                    description="Timestamp when the album was created"
                                )

    @field_serializer('image_url')
    def serialize_image_url(self, value: Optional[HttpUrl], _info):
        if not value:
            return None
        return str(value)

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
    }
