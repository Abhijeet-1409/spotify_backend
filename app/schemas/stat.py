from pydantic import BaseModel, Field


class Stats(BaseModel):
    total_albums: int = Field(
        title="Total Albums",
        description="The total number of albums in the database."
    )
    total_songs: int = Field(
        title="Total Songs",
        description="The total number of songs in the database."
    )
    total_users: int = Field(
        title="Total Users",
        description="The total number of registered users."
    )
    total_artists: int = Field(
        title="Total Artists",
        description="The number of unique artists across songs and albums."
    )
