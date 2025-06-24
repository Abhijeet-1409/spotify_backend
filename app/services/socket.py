from typing import Any, Optional

from pymongo.results import InsertOneResult

from app.models.message import MessageDB
from app.schemas.message import MessageOut
from app.db.connection import DatabaseConnection


class SocketService():

    _instance = None
    _initialized= False

    def __new__(cls,*args,**kwargs):
        if not cls._instance:
            cls._instance = super(SocketService,cls).__new__(cls)
        return cls._instance


    def __init__(self, db_instance: DatabaseConnection):
        if SocketService._initialized:
            return
        self.user_sockets = dict()
        self.user_activities = dict()
        self.db_instance = db_instance
        SocketService._initialized = True


    async def handle_message(self, sender_id: str, receiver_id: str, content: str) -> dict:

        message: MessageDB = MessageDB(sender_id=sender_id,receiver_id=receiver_id,content=content)
        insert_result: InsertOneResult = await self.db_instance.messages.insert_one(message.model_dump(by_alias=True))

        if not insert_result.inserted_id:
            raise Exception("Internal server error.")

        message_dict = message.model_dump()
        message_out = MessageOut(**message_dict)

        return message_out.model_dump(mode="json",by_alias=True)


    def remove_user(self, sid:str) -> Optional[str]:
        removed_user_id: Optional[str] = None

        for user_id, user_sid in self.user_sockets.items():
            if user_sid == sid:
                removed_user_id = user_id

        if removed_user_id:
            self.user_sockets.pop(removed_user_id)
            self.user_activities.pop(removed_user_id)

        return removed_user_id
