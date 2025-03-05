from pydantic import BaseModel,Field
from datetime import datetime, timezone 


class MessageDB(BaseModel) :
    sender_id: str = Field(title="Sender Id",description="Clerk id of the sender")
    receiver_id: str = Field(title="Receiver Id",description="Clerk id of the receiver")
    created_at: datetime = Field(
                                    default_factory=lambda: datetime.now(timezone.utc), 
                                    title="Created At",
                                    description="Timestamp when the message was created"
                                )
    

