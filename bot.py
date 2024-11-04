from sched import scheduler
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from mongoDB_database import get_all_users, add_new_user
from parser import get_cny_exchange_rate  # Импортируем ваш парсер

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Константа для предела курса
LOWER_THRESHOLD = 15.00


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_chat_id = update.message.chat_id  # получаем чат айди пользователя
    add_new_user(user_chat_id)
    logger.info(f"User with chat_id {user_chat_id} has started the bot.")

    await update.message.reply_text(
        "Hello! I`m a bot for getting a CNY exchange rate. Use /rate to get the current rate"
    )


# Функция для получения и отправки курса
async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        exchange_rate = get_cny_exchange_rate()  # Получаем курс
        await update.message.reply_text(exchange_rate)  # Отправляем курс пользователю
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await update.message.reply_text("Не удалось получить курс, попробуйте позже.")


async def notify_users(message: str, context: ContextTypes.DEFAULT_TYPE):
    # получаем всех пользователей из базы данных
    user_ids = get_all_users()

    # отправляем уведомление каждому пользователю
    for user_id in user_ids:
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
        )


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
                    message, context
                )  # отправляем сообщение всем пользователям

        else:
            logger.error("Buy rate not found in exchange rate message.")
    except Exception as e:
        logger.error(f"Error in rate check: {e}")


# Основная функция для запуска бота
def main() -> None:
    TOKEN = "7566668017:AAHme__gqzBTOgdMMC1HKpAIH2aQKJplyxk"

    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()
    scheduler = AsyncIOScheduler()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate))

    scheduler.add_job(
        check_rate, "interval", minutes=2, args=[application]
    )  # Проверка каждые 60 минут
    scheduler.start()

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
