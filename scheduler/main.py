import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db.session import async_session
from bot.main import get_bot
from utils.db.user import get_all_users_to_notify
from utils.parsers.gazprom import get_exchange_rate as get_gz_exchange_rate
from utils.parsers.google_finance import get_exchange_rate as get_google_exchange_rate
from utils.parsers.cbrf import get_exchange_rate as get_cbrf_exchange_rates
from utils.parsers import CBRFCodes, GoogleFinanceCodes
from utils.time_utils import utcnow
from utils.log import logger
from config import settings


async def send_message_handler():
    gz_rate = await get_gz_exchange_rate()
    google_rate_cny_to_rub = await get_google_exchange_rate(
        GoogleFinanceCodes.CNY, GoogleFinanceCodes.RUB
    )
    cbrf_rate_cny_to_rub = await get_cbrf_exchange_rates(CBRFCodes.CNY)
    msg = None

    if gz_rate:
        buy_rate = gz_rate.value
        logger.info(
            "Fetched Gazprombank buy rate {} - {}".format(gz_rate.date, buy_rate)
        )
        if buy_rate <= settings.LOWER_THRESHOLD:
            msg = "🔔 Alert! CNY **Gazprombank** Rate:\n💹Buy: {}₽, which is below {}₽".format(
                buy_rate, settings.LOWER_THRESHOLD
            )

    if google_rate_cny_to_rub:
        buy_rate = google_rate_cny_to_rub.value
        logger.info(
            "Fetched Google Finance buy rate {} - {}".format(
                google_rate_cny_to_rub.date, buy_rate
            )
        )
        if buy_rate <= settings.LOWER_THRESHOLD:
            new_msg = "🔔 Alert! CNY **Google Finance** Exchange Rate:\n💹Buy: {}₽, which is below {}₽".format(
                buy_rate, settings.LOWER_THRESHOLD
            )
            if msg is None:
                msg = new_msg
            else:
                msg += "\n\n" + new_msg

    if cbrf_rate_cny_to_rub:
        buy_rate = cbrf_rate_cny_to_rub.value
        logger.info(
            "Fetched CBRF buy rate {} - {}".format(cbrf_rate_cny_to_rub.date, buy_rate)
        )
        if buy_rate <= settings.LOWER_THRESHOLD:
            new_msg = "🔔 Alert! CNY **Central Bank of Russian Federation** Exchange Rate:\n💹Buy: {}₽, which is below {}₽".format(
                buy_rate, settings.LOWER_THRESHOLD
            )
            if msg is None:
                msg = new_msg
            else:
                msg += "\n\n" + new_msg

    if msg is not None:
        async with async_session() as session:
            users = await get_all_users_to_notify(session)
            if users is not None:
                bot = get_bot()
                for user in users:
                    try:
                        await bot.send_message(
                            chat_id=user.id, text=msg, parse_mode="Markdown"
                        )
                        logger.info(
                            "Message has been successfully delivered to user with id {}".format(
                                user.id
                            )
                        )
                    except Exception as e:
                        logger.warn(
                            "Failed to deliver message to user with id {}, as the error occurred: {}".format(
                                user.id, e
                            )
                        )


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
