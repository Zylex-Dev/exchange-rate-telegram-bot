import motor.motor_asyncio
from contextlib import asynccontextmanager
from pymongo.errors import ConnectionFailure
from utils.log import logger
from config import settings


class MongoSession:
    def __init__(self, uri: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[settings.MONGO_DB_NAME]

    async def __aenter__(self):
        logger.info(f"Connecting to MongoDB using URI: {settings.MONGO_DB_URI}")
        try:
            await self.client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("Disconnecting from MongoDB")
        self.client.close()
        if exc_type:
            logger.error(f"An error occurred: {exc_val}")


@asynccontextmanager
async def get_session():
    async with MongoSession(settings.MONGO_DB_URI) as session:
        yield session.db


async_session = get_session
