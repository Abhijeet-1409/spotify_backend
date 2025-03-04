from datetime import datetime, timezone 
from pydantic import BaseModel,EmailStr,HttpUrl,Field

class UserDB(BaseModel):
    _id: str = Field(title="_id",description="clerkId value is used as user's _id")
    username: str = Field(title="Username",description="User's username must be unique")
    email: EmailStr = Field(title="Email",description="User's email must be unique")
    image_url: HttpUrl = Field(title="Image Url",description="User's profile image")
    created_at: datetime = Field(
                                    default_factory=lambda: datetime.now(timezone.utc), 
                                    title="Created At",
                                    description="Timestamp when the user was created"
                                )
