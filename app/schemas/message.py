from bson import ObjectId

from datetime import datetime

from pydantic import Field, field_serializer

from app.models.message import MessageDB

class MessageOut(MessageDB):
    id: ObjectId = Field(title="Id",description="message's Id",alias="_id")
    sender_id: str = Field(title="Sender Id",description="Clerk id of the sender",alias="senderId")
    receiver_id: str = Field(title="Receiver Id",description="Clerk id of the receiver",alias="receiverId")
    created_at: datetime = Field(
                                    title="Created At",
                                    description="Timestamp when the message was created",
                                    alias="createdAt"
                                )

    @field_serializer('id')
    def serialize_id(self, value: ObjectId, _info) -> str:
        return str(value)

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat()