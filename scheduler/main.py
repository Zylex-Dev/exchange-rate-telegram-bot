import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db.session import async_session
from bot.main import get_bot
from utils.db.user import get_all_users_to_notify
from utils.gz_utils import get_gz_exchange_rate
from utils.time_utils import utcnow
from utils.log import logger
from config import settings


async def send_message_handler():
    result = await get_gz_exchange_rate()
    if result:
        buy_rate, date = float(result[1]), result[2]
        logger.info("Fetched buy rate {} - {}".format(date, buy_rate))
        if buy_rate <= settings.LOWER_THRESHOLD:
            async with async_session() as session:
                users = await get_all_users_to_notify(session)
            if users is not None:
                bot = get_bot()
                for user in users:
                    try:
                        await bot.send_message(
                            chat_id=user.id,
                            text="ПОКУПАТЬ ЮАНЬ, ОН МЕНЬШЕ {} РУБЛЕЙ!!!".format(
                                settings.LOWER_THRESHOLD
                            ),
                        )
                        logger.info(
                            "Message has been successfully delievered to user with id {}".format(
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
