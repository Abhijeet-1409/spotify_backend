from typing import Any

from fastapi import HTTPException, status, UploadFile

from app.errors.exceptions import InternalServerError

import cloudinary.api
import cloudinary.uploader
from cloudinary.exceptions import (
    NotAllowed as CloudinaryNotAllowed,
    BadRequest as CloudinaryBadRequest,
    Error as CloudinaryBaseError,
    NotFound as CloudinaryNotFound,
)


def sync_cloudinary_file_upload(file: UploadFile, file_type: str, id: str):
    try:
        file_response = cloudinary.uploader.upload(file.file, resource_type=file_type, folder=id)
        return file_response

    except CloudinaryBadRequest as cloudinary_bad_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload failed: Only {file_type} files are accepted."
        ) from cloudinary_bad_request

    except CloudinaryNotAllowed as cloudinary_not_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upload failed: This file is not allowed."
        ) from cloudinary_not_allowed

    except CloudinaryBaseError as cloudinary_base_error:
        raise IndentationError() from cloudinary_base_error

    except Exception as err:
        raise InternalServerError() from err


def delete_cloudinary_resource_based_on_id(id: str):
    try :

        prefix = f"{id}/"
        response_image = cloudinary.api.delete_resources_by_prefix(prefix=prefix, resource_type="image")
        response_audio = cloudinary.api.delete_resources_by_prefix(prefix=prefix, resource_type="video")
        response_folder = cloudinary.api.delete_folder(id)

    except CloudinaryNotFound as cloudinary_not_found:
        # pass # add exception to the logs later
        print("cloudinary_not_found",cloudinary_not_found)
    except CloudinaryBadRequest as cloudinary_bad_request:
        # pass # add exception to the logs later
        print("cloudinary_bad_request",cloudinary_bad_request)
    except Exception as err:
        # pass # add exception to the logs later
        print("err",Exception)


def delete_album_and_related_resources(album_id: str, song_ids: list[str]):

    delete_cloudinary_resource_based_on_id(id=album_id)

    for id in song_ids:
        delete_cloudinary_resource_based_on_id(id=id)


def album_doc_to_dict(album_doc: Any) -> dict:
    album_dict: dict = dict()
    album_dict['_id'] = album_doc['_id']
    album_dict['title'] = album_doc['title']
    album_dict['songs'] = album_doc['songs']
    album_dict['artist'] = album_doc['artist']
    album_dict['image_url'] = album_doc['image_url']
    album_dict['created_at'] = album_doc['created_at']
    album_dict['release_year'] = album_doc['release_year']

    return album_dict


def song_doc_to_dict(song_doc: Any) -> dict:
    song_dict: dict = dict()
    song_dict['_id'] = song_doc['_id']
    song_dict['title'] = song_doc['title']
    song_dict['artist'] = song_doc['artist']
    song_dict['album_id'] = song_doc['album_id']
    song_dict['duration'] = song_doc['duration']
    song_dict['image_url'] = song_doc['image_url']
    song_dict['audio_url'] = song_doc['audio_url']
    song_dict['created_at'] = song_doc['created_at']

    return song_dict