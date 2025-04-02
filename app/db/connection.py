from app.core.config import Settings
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase,AsyncIOMotorCollection

class DatabaseConnection() :
    _instance = None

    def __new__(cls, settings: Settings) :
        if cls._instance is None :
            cls._instance = super(DatabaseConnection,cls).__new__(cls)
            cls._instance._init_db(settings)
        return cls._instance

    def _init_db(self, settings: Settings):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URI)
        self.db: AsyncIOMotorDatabase = self.client.get_database(settings.MONGO_DBNAME)
        self.users: AsyncIOMotorCollection = self.db.get_collection("users")
        self.albums: AsyncIOMotorCollection = self.db.get_collection("albums")
        self.songs: AsyncIOMotorCollection = self.db.get_collection("songs")
        self.messages: AsyncIOMotorCollection = self.db.get_collection("messages")

    async def create_index(self) -> None:
        await self.users.create_index([("email", 1)], unique=True)
        return None

    def close_connection(self) :
        self.client.close()


