from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
from parser import get_cny_exchange_rate  # Импортируем ваш парсер

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


# Основная функция для запуска бота
def main() -> None:
    # Вставьте свой токен, полученный от BotFather
    TOKEN = "7566668017:AAHme__gqzBTOgdMMC1HKpAIH2aQKJplyxk"

    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
