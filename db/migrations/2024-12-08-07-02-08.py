import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from db.session import async_session
from utils.db.user import get_users_collection


logger = logging.getLogger(__name__)


async def upgrade(session: AsyncIOMotorDatabase):
    user_collection = await get_users_collection(session)

    try:
        update_result = await user_collection.update_many(
            {},
            {
                "$set": {
                    "gz_threshold": 14.00,
                    "google_threshold": 14.00,
                    "cbrf_threshold": 14.00,
                    "gz_notify": True,
                    "google_notify": True,
                    "cbrf_notify": True,
                }
            },
        )
        logger.debug(f"Updated {update_result.modified_count} documents.")

        delete_result = await user_collection.update_many(
            {}, {"$unset": {"last_alerted_rate": "", "notify": ""}}
        )
        logger.debug(f"Unset {delete_result.modified_count} documents.")
    except Exception as e:
        logger.error(f"An error occurred during upgrade: {e}")
        raise


async def downgrade(session: AsyncIOMotorDatabase):
    user_collection = await get_users_collection(session)

    try:
        remove_fields_result = await user_collection.update_many(
            {},
            {
                "$unset": {
                    "gz_threshold": "",
                    "google_threshold": "",
                    "cbrf_threshold": "",
                    "gz_notify": "",
                    "google_notify": "",
                    "cbrf_notify": "",
                }
            },
        )
        logger.debug(
            f"Removed {remove_fields_result.modified_count} documents' new fields."
        )

        restore_fields_result = await user_collection.update_many(
            {},
            {
                "$set": {
                    "last_alerted_rate": None,
                    "notify": True,
                }
            },
        )
        logger.debug(
            f"Restored {restore_fields_result.modified_count} documents' old fields."
        )
    except Exception as e:
        logger.error(f"An error occurred during downgrade: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    async def main():
        async with async_session() as session:
            await upgrade(session)

    asyncio.run(main())
