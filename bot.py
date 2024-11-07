from sched import scheduler
import re
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from mongoDB_database import (
    get_all_users,
    add_new_user,
    remove_user,
    update_user_alert_rate,
)
from parser import get_cny_exchange_rate  # Импортируем ваш парсер


# Получаем токен Telegram бота из переменной окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Константа для предела курса
LOWER_THRESHOLD = 14.00


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_chat_id = update.message.chat_id  # получаем чат айди пользователя
    add_new_user(user_chat_id)
    logger.info(f"User with chat_id {user_chat_id} has started the bot.")

    await update.message.reply_text(
        "Hello! I`m a bot for getting a CNY exchange rate.\nUse /rate to get the current rate"
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_chat_id = update.message.chat_id  # получаем чат айди пользователя
    remove_user(user_chat_id)  # удаляем из базы данных
    logger.info(f"User with chat_id: {user_chat_id} has stopped the bot.")

    await update.message.reply_text(
        "You have been unsubcribed from the CNY exchange rate alerts.\nUse /start to get them again."
    )


# Функция для получения и отправки курса
async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        exchange_rate = get_cny_exchange_rate()  # Получаем курс
        await update.message.reply_text(exchange_rate)  # Отправляем курс пользователю
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await update.message.reply_text("Не удалось получить курс, попробуйте позже.")


async def notify_users(
    message: str, buy_rate: float, context: ContextTypes.DEFAULT_TYPE
):
    # Получаем всех пользователей и их последний зафиксированный курс
    users = get_all_users()

    for user in users:
        user_id = user["chat_id"]
        last_alerted_rate = user.get("last_alerted_rate")

        if last_alerted_rate != buy_rate:  # уведомление только если курс изменился
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
            )
            # обновляем last_alerted_rate после отправки уведомления
            update_user_alert_rate(user_id, buy_rate)


# Функция для проверки курса и отправки уведомления
async def check_rate(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        exchange_rate = get_cny_exchange_rate()

        # Используем регулярное выражение для извлечения buy_rate
        match = re.search(r"💹Buy:\s*([\d.,]+)₽", exchange_rate)
        if match:
            buy_rate = float(
                match.group(1).replace(",", ".")
            )  # Извлекаем и конвертируем в float

            if buy_rate < LOWER_THRESHOLD:
                message = f"🔔 Alert! CNY Exchange Rate:\n💹Buy: {buy_rate}₽, which is below {LOWER_THRESHOLD}₽!"
                await notify_users(
                    message, buy_rate, context
                )  # Отправляем сообщение всем пользователям при изменении

        else:
            logger.error("Buy rate not found in exchange rate message.")
    except Exception as e:
        logger.error(f"Error in rate check: {e}")


# Основная функция для запуска бота
def main() -> None:
    # Создаем приложение
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    scheduler = AsyncIOScheduler()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("stop", stop))

    scheduler.add_job(
        check_rate, "interval", minutes=60, args=[application]
    )  # Проверка каждые 60 минут
    scheduler.start()

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
