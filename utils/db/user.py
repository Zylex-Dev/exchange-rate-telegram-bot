from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from typing import List, Optional

from utils.log import logger
from schemas.user import (
    UserCreateSchema,
    UserSchema,
    UserUpdateSchema,
    UserThresholdUpdateSchema,
    UserNotificationUpdateSchema,
)


async def get_users_collection(session: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
    return session.users


async def get_user_by_id(session, user_id: int) -> Optional[UserSchema]:
    users_collection = await get_users_collection(session)
    entity = await users_collection.find_one({"id": user_id})

    if entity:
        return UserSchema(**entity)


async def get_all_users(session: AsyncIOMotorDatabase) -> List[UserSchema]:
    users_collection = await get_users_collection(session)
    entities = await users_collection.find().to_list(length=None)

    if entities:
        return [UserSchema(**entity) for entity in entities]


async def get_all_users_to_notify(session: AsyncIOMotorDatabase):
    users_collection = await get_users_collection(session)
    entities = await users_collection.find(
        {"$or": [{"gz_notify": True}, {"google_notify": True}, {"cbrf_notify": True}]}
    ).to_list(length=None)

    if entities:
        return [UserSchema(**entity) for entity in entities]


async def create_or_update_user(
    session: AsyncIOMotorDatabase, schema: UserCreateSchema
):
    users_collection = await get_users_collection(session)
    exists = await users_collection.find_one({"id": schema.id})
    if not exists:
        await users_collection.insert_one(schema.model_dump())
    else:
        await users_collection.update_one(
            {"id": schema.id},
            {
                "$set": {
                    "username": schema.username,
                    "first_name": schema.first_name,
                    "last_name": schema.last_name,
                    "lang": schema.lang,
                },
            },
        )


async def update_user_alert_rate(
    session: AsyncIOMotorDatabase, user_id: int, rate: float
):
    users_collection = await get_users_collection(session)
    exists = await users_collection.find_one({"id": user_id})
    if exists:
        await users_collection.update_one(
            {"id": user_id}, {"$set": {"last_alerted_rate": rate}}
        )
    else:
        logger.warn("User with the given id {} does not exist".format(user_id))


async def update_user(session: AsyncIOMotorDatabase, schema: UserUpdateSchema):
    users_collection = await get_users_collection(session)
    exists = await users_collection.find_one({"id": schema.id})
    if exists:
        data = {}
        if schema.username:
            data.update({"username": schema.username})
        if schema.first_name:
            data.update({"first_name": schema.first_name})
        if schema.last_name:
            data.update({"last_name": schema.last_name})
        if schema.lang:
            data.update({"lang": schema.lang})
        if schema.notify is not None:
            data.update({"notify": schema.notify})

        await users_collection.update_one({"id": schema.id}, {"$set": data})
    else:
        logger.warn("User with the given id {} does not exist".format(schema.id))


async def update_user_notifications(
    session: AsyncIOMotorDatabase, schema: UserNotificationUpdateSchema
):
    users_collection = await get_users_collection(session)
    exists = await users_collection.find_one({"id": schema.id})
    if exists:
        data = {}
        if schema.gz_notify is not None:
            data.update({"gz_notify": schema.gz_notify})
        if schema.google_notify is not None:
            data.update({"google_notify": schema.google_notify})
        if schema.cbrf_notify is not None:
            data.update({"cbrf_notify": schema.cbrf_notify})

        await users_collection.update_one({"id": schema.id}, {"$set": data})
    else:
        logger.warn("User with the given id {} does not exist".format(schema.id))


async def update_user_threshold(
    session: AsyncIOMotorDatabase, schema: UserThresholdUpdateSchema
):
    users_collection = await get_users_collection(session)
    exists = await users_collection.find_one({"id": schema.id})
    if exists:
        data = {}
        if schema.gz_threshold is not None:
            data.update({"gz_threshold": schema.gz_threshold})
        if schema.google_threshold is not None:
            data.update({"google_threshold": schema.google_threshold})
        if schema.cbrf_threshold is not None:
            data.update({"cbrf_threshold": schema.cbrf_threshold})

        await users_collection.update_one({"id": schema.id}, {"$set": data})
    else:
        logger.warn("User with the given id {} does not exist".format(schema.id))
