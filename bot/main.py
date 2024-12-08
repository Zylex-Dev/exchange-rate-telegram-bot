import asyncio
import logging
from logging import getLogger
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from bot.routes.start import start_router
from bot.routes.rate import rate_router
from bot.routes.notification import notification_router
from bot.routes.donation import donation_router
from config import settings

log = getLogger("mitm")


def get_bot() -> Bot:
    return Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )


async def main():
    dp = Dispatcher()
    dp.include_routers(start_router, rate_router, notification_router, donation_router)

    log.info("Starting bot...")

    await dp.start_polling(get_bot())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
