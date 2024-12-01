import aiohttp

from schemas.gazprom import ExchangeRateSchema
from utils.log import logger
from config import settings


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
# yes, the use of headers is mandatory, since baka gazprom api checks for user-agent device


async def get_exchange_rate():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                settings.GAZPROMBANK_URL, ssl=False, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            content = item.get("content")
                            if content:
                                for rate_item in content:
                                    for rate in rate_item.get("items", []):
                                        if rate.get("ticker") == "CNY":
                                            return ExchangeRateSchema(
                                                value=rate.get("sell"),
                                                sell_rate=rate.get("buy"),
                                                date=rate.get("rateDate"),
                                            )

    except aiohttp.ClientError as e:
        logger.error(f"Error fetching the page: {e}")
