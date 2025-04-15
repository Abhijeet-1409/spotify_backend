from app.core.config import Settings
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase,AsyncIOMotorCollection

class DatabaseConnection() :
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs) :
        if not cls._instance :
            cls._instance = super(DatabaseConnection,cls).__new__(cls)
        return cls._instance

    def __init__(self, settings: Settings):
        if DatabaseConnection._initialized :
            return
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URI)
        self.db: AsyncIOMotorDatabase = self.client.get_database(settings.MONGO_DBNAME)
        self.users: AsyncIOMotorCollection = self.db.get_collection("users")
        self.albums: AsyncIOMotorCollection = self.db.get_collection("albums")
        self.songs: AsyncIOMotorCollection = self.db.get_collection("songs")
        self.messages: AsyncIOMotorCollection = self.db.get_collection("messages")
        DatabaseConnection._initialized = True

    async def create_index(self) -> None:
        await self.users.create_index([("email", 1)], unique=True)
        return None

    def close_connection(self) :
        self.client.close()


