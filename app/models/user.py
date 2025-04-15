from datetime import datetime, timezone
from pydantic import BaseModel,EmailStr,HttpUrl,Field,field_serializer

class UserDB(BaseModel):
    clerk_id: str = Field(title="Clerk Id",description="User's clerk id")
    full_name: str = Field(title="Full Name",description="User's full name")
    email: EmailStr = Field(title="Email",description="User's email must be unique")
    image_url: HttpUrl = Field(title="Image Url",description="User's profile image")
    created_at: datetime = Field(
                                    default_factory=lambda: datetime.now(timezone.utc),
                                    title="Created At",
                                    description="Timestamp when the user was created"
                                )

    @field_serializer('image_url')
    def serialize_image_url(self, value: HttpUrl, _info):
        return str(value)

    model_config = {
        "extra": "ignore",
        "populate_by_name": True,
        'arbitrary_types_allowed': True,
    }
