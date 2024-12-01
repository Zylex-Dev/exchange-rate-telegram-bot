from aiohttp import ClientSession
import xml.etree.ElementTree as ET
from typing import Optional

from schemas.cbrf import ExchangeRateSchema
from config import settings


async def get_exchange_rate(currency_name: str) -> Optional[ExchangeRateSchema]:
    async with ClientSession() as client:
        result = await client.get(url=settings.CBRF_URL, ssl=False)
        response = await result.read()

        root = ET.fromstring(response)
        date = root.attrib.get("Date")

        for valute in root.findall("Valute"):
            char_code = valute.find("CharCode").text
            if char_code == currency_name:
                value = valute.find("Value").text
                return ExchangeRateSchema(
                    currency=currency_name,
                    value=float(value.replace(",", ".")),
                    date=date,
                )


async def main():
    from utils.parsers import CBRFCodes

    result = await get_exchange_rate(CBRFCodes.USD)

    if result:
        print(f"Date: {result.date}, Currency: {result.currency}, Rate: {result.value}")
    else:
        print("Currency not found.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
