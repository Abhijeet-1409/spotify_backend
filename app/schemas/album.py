from pydantic import BaseModel, Field

class AlbumIn(BaseModel):
    title: str = Field(title="Title",description="Album's title")
    artist: str = Field(title="Artist",description="Album's artist")
    release_year: int = Field(title="Release Year",description="Album's release year")
