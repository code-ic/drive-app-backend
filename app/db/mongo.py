from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(
    settings.MONGO_URI
    # server_api={"version": "1"}  # Optional: ServerApi('1')
)

db = client[settings.MONGO_DB_NAME]