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
        cloudinary.api.delete_resources_by_prefix(prefix=prefix)
        cloudinary.api.delete_folder(id)

    except CloudinaryNotFound as cloudinary_not_found:
        pass # add exception to the logs later
    except CloudinaryBadRequest as cloudinary_bad_request:
        pass # add exception to the logs later
    except Exception as err:
        pass # add exception to the logs later