from bson import ObjectId

from datetime import datetime, timezone

from pydantic import BaseModel,Field


class MessageDB(BaseModel) :
    id: ObjectId = Field(default_factory=lambda: ObjectId(),title="Id",description="message's Id",alias="_id")
    sender_id: str = Field(title="Sender Id",description="Clerk id of the sender")
    receiver_id: str = Field(title="Receiver Id",description="Clerk id of the receiver")
    content: str = Field(title="Content",description="Message's Content")
    created_at: datetime = Field(
                                    default_factory=lambda: datetime.now(timezone.utc),
                                    title="Created At",
                                    description="Timestamp when the message was created",
                                )

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
    }
