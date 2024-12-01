import aiohttp
import asyncio
from datetime import datetime
from typing import Tuple, Optional

from utils.log import logger
from config import settings


async def get_exchange_rate(base_currency, target_currency) -> Optional[float]:
    today_date = datetime.today().strftime("%Y-%m-%d")
    url = f"{settings.GOOGLE_FINANCE_URL.format(date=today_date)}/{base_currency}.json"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                response.raise_for_status()
                data = await response.json()

                if target_currency in data[base_currency]:
                    exchange_rate = data[base_currency][target_currency]
                    logger.info(
                        f"Rate {base_currency} to {target_currency} on {today_date}: {exchange_rate}"
                    )
                    return exchange_rate
                else:
                    logger.error(
                        f"Couldn't find a rate for {target_currency} in {base_currency} on {today_date}."
                    )
    except aiohttp.ClientError as e:
        logger.error(f"Error when requesting data: {e}")


async def get_exchange_rates() -> Tuple[float, float, str]:
    today_date = datetime.today().strftime("%Y-%m-%d")
    usd_to_rub = await get_exchange_rate("usd", "rub")
    cny_to_rub = await get_exchange_rate("cny", "rub")

    return usd_to_rub, cny_to_rub, today_date


async def main():
    usd_to_rub, cny_to_rub, today_date = await get_exchange_rates()
    logger.info(f"Received rates: USD/RUB = {usd_to_rub}, CNY/RUB = {cny_to_rub}")


if __name__ == "__main__":
    asyncio.run(main())
