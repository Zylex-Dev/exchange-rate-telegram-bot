import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db.session import async_session
from bot.main import get_bot
from utils.parsers.gazprom import get_exchange_rate as get_gz_exchange_rate
from utils.parsers.google_finance import get_exchange_rate as get_google_exchange_rate
from utils.parsers.cbrf import get_exchange_rate as get_cbrf_exchange_rates
from utils.parsers import CBRFCodes, GoogleFinanceCodes, GazprombankCodes
from utils.db.user import get_all_users_to_notify
from utils.time_utils import utcnow
from utils.log import logger
from config import settings


async def fetch_exchange_rates() -> tuple:
    tasks = [
        asyncio.create_task(get_gz_exchange_rate(GazprombankCodes.CNY)),
        asyncio.create_task(
            get_google_exchange_rate(GoogleFinanceCodes.CNY, GoogleFinanceCodes.RUB)
        ),
        asyncio.create_task(get_cbrf_exchange_rates(CBRFCodes.CNY)),
    ]

    return await asyncio.gather(*tasks)


async def send_message_handler():
    gz_rate, google_rate_cny_to_rub, cbrf_rate_cny_to_rub = await fetch_exchange_rates()

    rate_data = {
        "gz": gz_rate,
        "google": google_rate_cny_to_rub,
        "cbrf": cbrf_rate_cny_to_rub,
    }
    source_name = {
        "gz": "Gazprombank",
        "google": "Google Finance",
        "cbrf": "Central Bank of Russian Federation",
    }

    async with async_session() as session:
        users = await get_all_users_to_notify(session)

        if users:
            bot = get_bot()
            tasks = []

            for rate_name, rate in rate_data.items():
                if rate:
                    buy_rate = rate.value
                    logger.info(
                        f"Fetched {rate_name} buy rate: {buy_rate} - {rate.date}"
                    )

                    for user in users:
                        threshold_field = f"{rate_name}_threshold"
                        notify_field = f"{rate_name}_notify"

                        if getattr(user, notify_field) and buy_rate <= getattr(
                            user, threshold_field
                        ):
                            message = f"🔔 Alert! CNY **{source_name[rate_name]}** Exchange Rate:\n💹Buy: {buy_rate:.2f}₽"

                            tasks.append(
                                asyncio.create_task(
                                    bot.send_message(
                                        chat_id=user.id,
                                        text=message,
                                        parse_mode="Markdown",
                                    )
                                )
                            )

            if tasks:
                await asyncio.gather(*tasks)


async def main():
    logger.info(f"Scheduler is starting at {utcnow()}...")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_message_handler,
        trigger=IntervalTrigger(minutes=settings.SCHEDULER_DELAY),
        id="send_message_handler",
        replace_existing=True,
    )
    scheduler.start()

    try:
        while True:
            logger.info(f"Scheduler invoked at {utcnow()}")
            await asyncio.sleep(15)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())
