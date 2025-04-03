from bson import ObjectId

from typing import Optional

from pydantic import BaseModel, Field, field_validator

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
        data['album_id'] = ObjectId(album_id) if album_id else album_id
        return data
