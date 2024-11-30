import aiohttp

from utils.log import logger


async def get_gz_exchange_rate():
    url = "https://www.gazprombank.ru/rest/exchange/rate?ab_segment=segment08&cityId=617&version=3&lang=ru"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as response:
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
                                            sell_rate = rate.get("buy")
                                            buy_rate = rate.get("sell")
                                            rate_date = rate.get("rateDate")
                                            return sell_rate, buy_rate, rate_date

    except aiohttp.ClientError as e:
        logger.error(f"Error fetching the page: {e}")
