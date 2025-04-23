from typing import List

from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorCursor

from fastapi import HTTPException, status

from app.schemas.song import SongOut
from app.schemas.album import AlbumOut, AlbumDetailOut
from app.db.connection import DatabaseConnection
from app.errors.exceptions import InternalServerError
from app.utils.utils import album_doc_to_dict, song_doc_to_dict


class AlbumService():

    def __init__(self, db_instance: DatabaseConnection):
        self.db_instance = db_instance

    async def fetch_all_albums(self) -> List[AlbumOut]:
        try :

            album_cursor: AsyncIOMotorCursor = self.db_instance.albums.find()

            album_doc_list = await album_cursor.to_list()

            album_dict_list: List[dict] = [ album_doc_to_dict(album_doc) for album_doc in album_doc_list ]
            album_out_list: List[AlbumOut] = [ AlbumOut(**album_dict) for album_dict in album_dict_list ]

            return album_out_list

        except HTTPException as http_err:
            raise http_err

        except Exception as err :
            raise InternalServerError() from err


    async def fetch_album_by_id(self, album_id: str) -> AlbumDetailOut:
        try :

            if not ObjectId.is_valid(album_id):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{album_id} is not a valid id."
                )

            album_object_id = ObjectId(album_id)

            album_doc = await self.db_instance.albums.find_one({"_id": album_object_id})

            if not album_doc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Album with a id {album_id} does not exists."
                )

            album_dict: dict = album_doc_to_dict(album_doc)
            song_cursor: AsyncIOMotorCursor = self.db_instance.songs.find({'album_id': album_object_id})

            song_doc_list = await song_cursor.to_list()

            song_dict_list: List[dict] = [ song_doc_to_dict(song_doc) for song_doc in song_doc_list ]
            song_out_list: List[SongOut] = [ SongOut(**song_dict) for song_dict in song_dict_list]
            album_dict['songs'] = song_out_list
            album_detial_out = AlbumDetailOut(**album_dict)

            return album_detial_out

        except HTTPException as http_err:
            raise http_err

        except Exception as err :
            raise InternalServerError() from err