from datetime import datetime

from bson import ObjectId

from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_serializer

from app.models.user import UserDB

class UserIn(BaseModel):
    clerk_id: str = Field(title="Clerk Id",description="User's clerk id",alias="clerkId")
    first_name: str = Field(title="First Name",description="User's first name",alias="firstName")
    last_name: str = Field(title="Last Name",description="User's last name",alias="lastName")
    email: EmailStr = Field(title="Email",description="User's email must be unique")
    image_url: HttpUrl = Field(title="Image Url",description="User's profile image",alias="imageUrl")

    model_config ={
        "populate_by_name": True,
    }

class UserOut(UserDB):
    id: ObjectId = Field(title="Id",description="User's db id",alias="_id")
    clerk_id: str = Field(title="Clerk Id",description="User's clerk id",alias="clerkId")
    full_name: str = Field(title="Full Name",description="User's full name",alias="fullName")
    image_url: HttpUrl = Field(title="Image Url",description="User's profile image",alias="imageUrl")
    created_at: datetime = Field(title="Created At",description="Timestamp when the user was created",alias="createdAt")

    @field_serializer('id')
    def serialize_id(self, value: ObjectId, _info) -> str:
        return str(value)

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        return value.isoformat()