from pymongo import MongoClient

# подключение к локальной базе данных
client = MongoClient("mongodb://localhost:27017/")
db = client["telegram_bot_db"]  # название базы данных
users_collection = db["users"]  # коллекция users для хранения chat_id


def get_all_users():
    # Возвращаем список всех chat_id в коллекции
    return [user["chat_id"] for user in users_collection.find()]


def add_new_user(user_chat_id):
    # добавляем пользователя в базу данных, если его еще нет
    if not users_collection.find_one({"chat_id": user_chat_id}):
        users_collection.insert_one({"chat_id": user_chat_id})


def remove_user(user_chat_id):
    # удаляем пользователя по чат айди из базы данных
    users_collection.delete_one({"chat_id": user_chat_id})
