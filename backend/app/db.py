from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

_client: AsyncIOMotorClient | None = None

async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongo_url)

async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        _client = None

def get_db() -> AsyncIOMotorDatabase:
    return _client[settings.mongo_db]
