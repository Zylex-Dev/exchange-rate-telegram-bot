import aiohttp
import asyncio
from datetime import datetime
from typing import Optional

from utils.log import logger
from utils.parsers import GoogleFinanceCodes
from schemas.google_finance import ExchangeRateSchema
from config import settings


async def get_exchange_rate(
    base_currency: GoogleFinanceCodes, target_currency: GoogleFinanceCodes
) -> Optional[ExchangeRateSchema]:
    today_date = datetime.today().strftime("%Y-%m-%d")
    url = f"{settings.GOOGLE_FINANCE_URL.format(date=today_date)}/{base_currency.value}.json"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                response.raise_for_status()
                data = await response.json()

                if target_currency.value in data[base_currency.value]:
                    exchange_rate = data[base_currency.value][target_currency.value]
                    logger.info(
                        f"Rate {base_currency.value} to {target_currency.value} on {today_date}: {exchange_rate}"
                    )
                    return ExchangeRateSchema(
                        currency=base_currency.value,
                        value=float(exchange_rate),
                        date=today_date,
                    )
                else:
                    logger.error(
                        f"Couldn't find a rate for {target_currency.value} in {base_currency.value} on {today_date}."
                    )
    except aiohttp.ClientError as e:
        logger.error(f"Error when requesting data: {e}")
