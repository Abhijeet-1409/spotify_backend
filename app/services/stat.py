import asyncio

from fastapi import HTTPException

from motor.motor_asyncio import AsyncIOMotorCursor

from app.schemas.stat import Stats
from app.db.connection import DatabaseConnection
from app.errors.exceptions import InternalServerError


class StatService():

    def __init__(self, db_instance: DatabaseConnection):
        self.db_instance = db_instance

    async def fetch_stats(self) -> Stats:
        try :

            pipeline = [
                {
                    "$unionWith": {
                        "coll": "albums",
                        "pipeline": []
                    }
                },
                {
                    "$group": {
                        "_id": "$artist"
                    }
                },
                {
                    "$count": "count"
                }
            ]

            unique_artist_cursor: AsyncIOMotorCursor = self.db_instance.songs.aggregate(pipeline=pipeline)

            song_count_coro = self.db_instance.songs.count_documents({})
            user_count_coro = self.db_instance.users.count_documents({})
            album_count_coro = self.db_instance.albums.count_documents({})
            unique_artists_coro = unique_artist_cursor.to_list(length=1)

            song_count, user_count, album_count, unique_artists = await asyncio.gather(
                song_count_coro,
                user_count_coro,
                album_count_coro,
                unique_artists_coro
            )

            unique_artist_count = unique_artists[0]['count'] if unique_artists else 0

            stats_instance: Stats = Stats(
                total_albums=album_count,
                total_songs=song_count,
                total_users=user_count,
                total_artists=unique_artist_count
            )

            return stats_instance

        except HTTPException as http_err :
            raise http_err

        except Exception as err :
            raise InternalServerError() from err
