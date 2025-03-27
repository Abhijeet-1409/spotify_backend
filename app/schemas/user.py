from pydantic import BaseModel, Field, EmailStr, HttpUrl

class UserIn(BaseModel):
    _id: str = Field(title="_id",description="clerkId value is used as user's _id")
    username: str = Field(title="Username",description="User's username must be unique")
    email: EmailStr = Field(title="Email",description="User's email must be unique")
    image_url: HttpUrl = Field(title="Image Url",description="User's profile image")