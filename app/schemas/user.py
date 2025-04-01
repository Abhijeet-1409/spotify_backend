from pydantic import BaseModel, Field, EmailStr, HttpUrl

class UserIn(BaseModel):
    _id: str = Field(title="_id",description="clerkId value is used as user's _id")
    first_name: str = Field(title="First Name",description="User's first name")
    last_name: str = Field(title="Last Name",description="User's last name")
    email: EmailStr = Field(title="Email",description="User's email must be unique")
    image_url: HttpUrl = Field(title="Image Url",description="User's profile image")