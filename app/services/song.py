from typing import List

from fastapi import HTTPException

from motor.motor_asyncio import AsyncIOMotorCursor

from app.schemas.song import SongOut
from app.utils.utils import song_doc_to_dict
from app.db.connection import DatabaseConnection
from app.errors.exceptions import InternalServerError


class SongService():

    def __init__(self, db_instance: DatabaseConnection):
        self.db_instance = db_instance

    async def _fetch_random_songs(self, count: int) -> List[SongOut]:
        try :
            pipeline = [{ "$sample": { "size": count } }]
            song_cursor:  AsyncIOMotorCursor = self.db_instance.songs.aggregate(pipeline=pipeline)

            song_doc_list = await song_cursor.to_list(length=count)

            song_dict_list: List[dict] = [ song_doc_to_dict(song_doc) for song_doc in song_doc_list ]
            song_out_list: List[SongOut] = [ SongOut(**song_dict) for song_dict in song_dict_list ]

            return song_out_list

        except HTTPException as http_err :
            raise http_err

        except Exception as err :
            raise InternalServerError() from err


    async def fetch_all_songs(self) -> List[SongOut]:
        try :
            song_cursor: AsyncIOMotorCursor = self.db_instance.songs.find()

            song_doc_list = await song_cursor.to_list()

            song_dict_list: List[dict] = [ song_doc_to_dict(song_doc) for song_doc in song_doc_list ]
            song_out_list: List[SongOut] = [ SongOut(**song_dict) for song_dict in song_dict_list ]

            return song_out_list

        except HTTPException as http_err :
            raise http_err

        except Exception as err :
            raise InternalServerError() from err


    async def fetch_featured_songs(self) -> List[SongOut]:
        try :
            song_out_list: List[SongOut] = await self._fetch_random_songs(count=6)

            return song_out_list

        except HTTPException as http_err :
            raise http_err

        except Exception as err :
            raise InternalServerError() from err


    async def fetch_made_for_you_songs(self) -> List[SongOut]:
        try :
            song_out_list: List[SongOut] = await self._fetch_random_songs(count=4)

            return song_out_list

        except HTTPException as http_err :
            raise http_err

        except Exception as err :
            raise InternalServerError() from err


    async def fetch_trending_songs(self) -> List[SongOut]:
        try :
            song_out_list: List[SongOut] = await self._fetch_random_songs(count=4)

            return song_out_list

        except HTTPException as http_err :
            raise http_err

        except Exception as err :
            raise InternalServerError() from err