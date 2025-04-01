from fastapi import HTTPException

from pymongo.results import InsertOneResult

from app.models.user import UserDB
from app.schemas.user import UserIn
from app.db.connection import DatabaseConnection
from app.errors.exceptions import InternalServerError

class AuthService():

    def __init__(self, db_instance: DatabaseConnection):
        self.db_instance = db_instance

    async def auth_callback(self, user_auth_data: UserIn) -> dict:
        try :

            user_doc = await self.db_instance.users.find_one({"_id": user_auth_data._id})

            if not user_doc:
                user_db_dict = user_auth_data.model_dump()
                user_db_dict['full_name'] = user_auth_data.first_name + user_auth_data.last_name
                user: UserDB = UserDB(**user_db_dict)
                insert_result: InsertOneResult = await self.db_instance.users.insert_one(user.model_dump())

                if not insert_result.inserted_id:
                    raise InternalServerError()

            return {'success': True}

        except HTTPException as http_err:
            raise http_err

        except Exception as err:
            raise InternalServerError() from err
