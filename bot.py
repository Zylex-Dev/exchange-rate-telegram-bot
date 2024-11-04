from sched import scheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from parser import get_cny_exchange_rate  # Импортируем ваш парсер

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Константа для предела курса
LOWER_THRESHOLD = 14.00
user_chat_id = (
    None  # Переменная для хранения chat_id пользователя, отправившего команду /start
)


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_chat_id
    user_chat_id = update.message.chat_id  # сохраняем чат айди пользователя
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


# Функция для проверки курса и отправки уведомления
async def check_rate(context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_chat_id
    if user_chat_id:  # Проверяем, задан ли chat_id
        try:
            exchange_rate = get_cny_exchange_rate()

            # Парсим курс из строки (ожидается, что buy_rate - это строка "Buy: XX.XX")
            buy_rate_str = exchange_rate.split("Buy: ")[1].split(" RUB")[0]
            buy_rate = float(buy_rate_str)

            if buy_rate < LOWER_THRESHOLD:
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=f"🔔 Alert! CNY Exchange Rate Buy is now {buy_rate} RUB, which is below {LOWER_THRESHOLD} RUB!",
                )
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
        check_rate, "interval", minute=60, args=[application]
    )  # Проверка каждые 60 минут
    scheduler.start()

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
