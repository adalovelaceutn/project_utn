from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings


client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    if client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return client


def get_collection():
    db = get_client()[settings.mongo_db_name]
    return db[settings.mongo_kolb_collection]


def get_kolb_collection():
    db = get_client()[settings.mongo_db_name]
    return db[settings.mongo_kolb_collection]


def get_users_collection():
    db = get_client()[settings.mongo_db_name]
    return db[settings.mongo_users_collection]


async def connect_to_mongo() -> None:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongo_uri)


async def close_mongo_connection() -> None:
    global client
    if client is not None:
        client.close()
        client = None
