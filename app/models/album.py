from bson import ObjectId
from datetime import datetime, timezone
from pydantic import BaseModel,HttpUrl,Field,field_serializer

class AlbumDB(BaseModel) :
    title: str = Field(title="Title",description="Album's title")
    artist: str = Field(title="Artist",description="Album's artist")
    image_url: HttpUrl = Field(title="Image Url",description="Album's cover image")
    release_year: int = Field(title="Release Year",description="Album's release year")
    songs: list[ObjectId] = Field(title="Songs",description="Album's Song")
    created_at: datetime = Field(
                                    default_factory=lambda: datetime.now(timezone.utc),
                                    title="Created At",
                                    description="Timestamp when the album was created"
                                )

    @field_serializer('image_url')
    def serialize_image_url(self, value: HttpUrl, _info):
        return str(value)

    model_config = {
        "arbitrary_types_allowed": True,
    }
