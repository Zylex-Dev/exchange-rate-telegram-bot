import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

MONGO_DB_URI = os.getenv("MONGO_DB_URI")
# Подключение к облачной базе данных MongoDB Atlas
client = MongoClient(MONGO_DB_URI, server_api=ServerApi("1"))


# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client["telegram_bot_db"]  # название базы данных
users_collection = db["users"]  # коллекция users для хранения chat_id


def get_all_users():
    # Возвращаем список всех chat_id и их данных в коллекции
    # return [user["chat_id"] for user in users_collection.find()]
    return list(users_collection.find())


def add_new_user(user_chat_id):
    # добавляем пользователя в базу данных, если его еще нет
    if not users_collection.find_one({"chat_id": user_chat_id}):
        users_collection.insert_one(
            {
                "chat_id": user_chat_id,
                "last_alerted_rate": None,  # поле для хранения курса последнего уведомления
            }
        )


def update_user_alert_rate(user_chat_id, rate):
    # обновляет курс последнего уведомления для пользователя
    users_collection.update_one(
        {"chat_id": user_chat_id}, {"$set": {"last_alerted_rate": rate}}
    )


def remove_user(user_chat_id):
    # удаляем пользователя по чат айди из базы данных
    users_collection.delete_one({"chat_id": user_chat_id})
