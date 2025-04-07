import os
from pydantic_settings import BaseSettings,SettingsConfigDict

# Get the current file's directory
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)

# Go up two level
project_directory = os.path.dirname(os.path.dirname(current_directory))

# Construct the path to the .env file
env_file_path = os.path.join(project_directory, '.env')

class Settings(BaseSettings) :
    APP_NAME: str # use .env file
    MONGO_USERNAME: str = "default_user" #  use env var
    MONGO_PASSWORD: str = "default_password" # use env var
    MONGO_DBNAME: str = "default_db" # use env var
    CLERK_SECRET_KEY: str = "default_clerk_secret_key" # use env var
    CLOUDINARY_SECRET_KEY: str = "default_cloudinary_secret_key" # use env var
    CLOUDINARY_API_KEY: str = "default_cloudianry_api_key" # use env var
    CLOUDINARY_CLOUD_NAME: str = "default_cloudinary_cloud_name" # use env var
    ADMIN_EMAIL: str = "default_admin_email" # use env file
    MAX_FILE_SIZE_MB: int = 10 # use env file

    @property
    def MONGO_URI(self) -> str:
        return f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@cluster0.4vupk.mongodb.net/{self.MONGO_DBNAME}?retryWrites=true&w=majority&appName=Cluster0"

    model_config = SettingsConfigDict(env_file=env_file_path,extra="allow")


