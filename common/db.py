from config import Config
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGODB_URL)
db = client[Config.MONGODB_DB]

collections = dict(
    articles=db.articles,
    users=db.users,
    hosts=db.hosts
)
