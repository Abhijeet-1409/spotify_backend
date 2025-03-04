from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone 
from pydantic import BaseModel,HttpUrl,Field

class SongDB(BaseModel):
    title: str = Field(title="Title",description="Song's title")
    artist: str = Field(title="Artist",description="Artist's Name")
    image_url: HttpUrl = Field(title="Image Url",description="Song's cover image")
    audio_url: HttpUrl = Field(title="Audio Url",description="Song's actual audio")
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
    
    class Config :
        arbitrary_types_allowed = True



    
