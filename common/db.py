from config import Config
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

db_client: AsyncIOMotorClient = None

async def connect_db():
    db_client = AsyncIOMotorClient(Config.MONGODB_URL)

async def get_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(Config.MONGODB_URL)
    db = client[Config.MONGODB_DB]
    return db

async def close_db():
    db_client.close()

collections = dict(
    articles="articles",
    users="users",
    hosts="hosts"
)
