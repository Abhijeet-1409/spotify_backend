import asyncio

from bson import ObjectId

from pymongo.results import InsertOneResult, UpdateResult

from fastapi import HTTPException, UploadFile, status, BackgroundTasks

from cloudinary.exceptions import Error as CloudinaryBaseError

from app.models.song import SongDB
from app.models.album import AlbumDB
from app.schemas.song import SongIn, SongOut
from app.schemas.album import AlbumIn, AlbumOut
from app.db.connection import DatabaseConnection
from app.errors.exceptions import (
    InternalServerError,
    SongInconsistencyError,
    AlbumInconsistencyError
)
from app.utils.utils import (
    sync_cloudinary_file_upload,
    delete_album_and_related_resources,
    delete_cloudinary_resource_based_on_id,
)


class AdminService():

    def __init__(self, db_instance: DatabaseConnection):
        self.db_instance = db_instance

    async def create_song(
            self,
            song_data: SongIn,
            image_file: UploadFile,
            audio_file: UploadFile,
            background_tasks: BackgroundTasks
        ) -> SongOut:
        try :

            song_db_dict = song_data.model_dump()
            album_id = song_db_dict['album_id']

            if album_id :
                album_doc = await self.db_instance.albums.find_one({"_id": album_id})

                if not album_doc :
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Album with id {song_data.album_id} don't exists."
                    )

            song: SongDB = SongDB(**song_db_dict)
            song_id = str(song.id)

            image_coro = asyncio.to_thread(sync_cloudinary_file_upload,image_file,"image",song_id)
            audio_coro = asyncio.to_thread(sync_cloudinary_file_upload,audio_file,"video",song_id)

            image_response, audio_response = await asyncio.gather(image_coro, audio_coro)

            song.image_url = image_response['secure_url']
            song.audio_url = audio_response['secure_url']

            insert_result: InsertOneResult = await self.db_instance.songs.insert_one(song.model_dump(by_alias=True))

            if not insert_result.inserted_id:
                raise SongInconsistencyError(song_id=song_id)

            if album_id :
                update_result: UpdateResult = await self.db_instance.albums.update_one(
                    {"_id": album_id},
                    {"$push": {"songs": insert_result.inserted_id}}
                )

                if update_result.modified_count < 1 :
                    await self.delete_song(song_id=song_id,background_tasks=background_tasks)
                    raise InternalServerError()

            song_out_dict = song.model_dump()
            song_out = SongOut(**song_out_dict)

            return song_out

        except HTTPException as http_err:
            cause = http_err.__cause__
            if isinstance(cause,CloudinaryBaseError):
                background_tasks.add_task(delete_cloudinary_resource_based_on_id,song_id)
            raise http_err

        except SongInconsistencyError as inconsistency_err:
            background_tasks.add_task(delete_cloudinary_resource_based_on_id,inconsistency_err.song_id)
            raise InternalServerError() from inconsistency_err

        except Exception as err:
            raise InternalServerError() from err


    async def delete_song(self, song_id: str, background_tasks: BackgroundTasks) -> dict:
        try :
            if not ObjectId.is_valid(song_id):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{song_id} is not a valid id."
                )

            song_object_id = ObjectId(song_id)

            song_doc = await self.db_instance.songs.find_one_and_delete({"_id": song_object_id})

            if not song_doc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Song with a id {song_id} does not exists."
                )

            if song_doc['album_id']:
                update_result: UpdateResult = await self.db_instance.albums.update_one(
                    {"_id": song_doc['album_id']},
                    {"$pull": {"songs": song_object_id}}
                )

                if update_result.modified_count < 1:
                    raise InternalServerError()

            background_tasks.add_task(delete_cloudinary_resource_based_on_id,song_id)

            return {"message": "Song deleted successfully"}

        except HTTPException as http_err :
            raise http_err

        except Exception as err:
            raise InternalServerError() from err


    async def create_album(
            self,
            album_data: AlbumIn,
            image_file: UploadFile,
            background_tasks: BackgroundTasks,
        ) -> AlbumOut :
        try :

            album_db_dict: dict = album_data.model_dump()
            album: AlbumDB = AlbumDB(**album_db_dict)
            album_id: str = str(album.id)

            image_response = await asyncio.to_thread(sync_cloudinary_file_upload,image_file,"image",album_id)

            album.image_url = image_response['secure_url']

            insert_result: InsertOneResult = await self.db_instance.albums.insert_one(album.model_dump(by_alias=True))

            if not insert_result.inserted_id:
                raise AlbumInconsistencyError(album_id=album_id)

            album_out_dict = album.model_dump()
            album_out = AlbumOut(**album_out_dict)

            return album_out

        except HTTPException as http_err:
            cause = http_err.__cause__
            if isinstance(cause,CloudinaryBaseError):
                background_tasks.add_task(delete_cloudinary_resource_based_on_id,album_id)
            raise http_err

        except AlbumInconsistencyError as inconsistency_err:
            background_tasks.add_task(delete_cloudinary_resource_based_on_id,inconsistency_err.album_id)
            raise InternalServerError() from inconsistency_err

        except Exception as err:
            raise InternalServerError() from err


    async def delete_album(self, album_id: str, background_tasks: BackgroundTasks) -> dict:
        try :
            if not ObjectId.is_valid(album_id):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{album_id} is not a valid id."
                )

            album_object_id = ObjectId(album_id)

            album_doc = await self.db_instance.albums.find_one_and_delete({"_id": album_object_id})

            if not album_doc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Song with a id {album_id} does not exists."
                )

            song_ids = album_doc['songs']
            song_str_ids = [str(id) for id in song_ids] if song_ids else []

            await self.db_instance.songs.delete_many({"_id": {"$in": song_ids}})

            background_tasks.add_task(delete_album_and_related_resources,album_id,song_str_ids)

            return {"message": "Song deleted successfully"}

        except HTTPException as http_err :
            raise http_err

        except Exception as err:
            raise InternalServerError() from err
