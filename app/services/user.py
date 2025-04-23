from typing import List

from fastapi import HTTPException

from motor.motor_asyncio import AsyncIOMotorCursor

from app.schemas.user import UserOut
from app.utils.utils import user_doc_to_dict
from app.db.connection import DatabaseConnection
from app.errors.exceptions import InternalServerError


class UserService():

    def __init__(self, db_instance: DatabaseConnection):
        self.db_instance = db_instance

    async def fetch_all_users(self, current_user_id: str) -> List[UserOut]:
        try :
            user_cursor: AsyncIOMotorCursor = self.db_instance.users.find({ 'clerk_id': { '$ne': current_user_id } })

            user_doc_list = await user_cursor.to_list()

            user_dict_list: List[dict] = [ user_doc_to_dict(user_doc) for user_doc in user_doc_list ]
            user_out_list: List[UserOut] = [ UserOut(**user_dict) for user_dict in user_dict_list ]

            return user_out_list

        except HTTPException as http_err :
            raise http_err

        except Exception as err :
            raise InternalServerError() from err