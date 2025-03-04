import os 
from pydantic_settings import BaseSettings,SettingsConfigDict

# Get the current file's directory
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)

# Go up two level
project_directory = os.path.dirname(os.path.dirname(current_directory))

# Construct the path to the .env file
env_file_path = os.path.join(project_directory, '.env')

class Setting(BaseSettings) :
    APP_NAME: str # use .env file
    MONGO_USERNAME: str = "default_user" #  use env var
    MONGO_PASSWORD: str = "default_password" # use env var
    MONGO_DBNAME: str = "default_db" # use env var

    @property 
    def MONGO_URI(self) -> str:
        return f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@cluster0.4vupk.mongodb.net/{self.MONGO_DBNAME}?retryWrites=true&w=majority&appName=Cluster0"

    model_config = SettingsConfigDict(env_file=env_file_path,extra="allow")


