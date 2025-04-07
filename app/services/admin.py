import asyncio

from bson import ObjectId

from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from fastapi import HTTPException, UploadFile, status, BackgroundTasks

from cloudinary.exceptions import Error as CloudinaryBaseError

from app.models.song import SongDB
from app.schemas.song import SongIn , SongOut
from app.errors.exceptions import InternalServerError, SongInconsistencyError
from app.db.connection import DatabaseConnection
from app.utils.utils import (
    sync_cloudinary_file_upload,
    delete_cloudinary_resource_based_on_id
)


class AdminService():

    def __init__(self, db_instance: DatabaseConnection):
        self.db_instance = db_instance

    async def create_song(self, image_file: UploadFile, audio_file: UploadFile, song_data: SongIn, background_tasks: BackgroundTasks) -> SongOut:
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

            image_response = await asyncio.to_thread(sync_cloudinary_file_upload,image_file,"image",song_id)
            audio_response = await asyncio.to_thread(sync_cloudinary_file_upload,audio_file,"video",song_id)

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


    async def delete_song(self, song_id: str, background_tasks: BackgroundTasks):
        try :
            if ObjectId.is_valid(song_id):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{song_id} is not a valid id."
                )

            song_object_id = ObjectId(song_id)

            song_doc = await self.db_instance.songs.find_one_and_delete({"_id", song_object_id})

            if not song_doc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Song with a id {song_id} does not exists."
                )

            background_tasks.add_task(delete_cloudinary_resource_based_on_id,song_id)

            update_result: UpdateResult = await self.db_instance.albums.update_one(
                {"_id": song_doc['album_id']},
                {"$pull": {"songs": song_object_id}}
            )

            if update_result.modified_count < 1:
                raise InternalServerError()

            return {"message": "Song deleted successfully"}

        except HTTPException as http_err :
            raise http_err

        except Exception as err:
            raise InternalServerError() from err
