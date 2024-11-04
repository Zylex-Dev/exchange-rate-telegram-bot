import requests
import json


def get_cny_exchange_rate() -> str:
    url = "https://www.gazprombank.ru/rest/exchange/rate?ab_segment=segment08&cityId=617&version=3&lang=ru"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка успешного выполнения запроса

        data = response.json()

        # Проверяем, является ли data списком
        if isinstance(data, list):
            for item in data:
                # Проверяем, что item является словарем и содержит ключ "content"
                if isinstance(item, dict):
                    content = item.get("content")
                    if content:  # Проверяем, что content не None и не пустой
                        for rate_item in content:
                            for rate in rate_item.get("items", []):
                                if rate.get("ticker") == "CNY":
                                    sell_rate = rate.get("buy")  # Курс покупки
                                    buy_rate = rate.get("sell")  # Курс продажи
                                    rate_date = rate.get(
                                        "rateDate"
                                    )  # Дата актуальности курса
                                    return f"CNY Exchange Rate - Buy: {buy_rate} RUB, Sell: {sell_rate} RUB\nDate: {rate_date}"

        return "CNY rate not found"
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return "Error fetching exchange rate"
