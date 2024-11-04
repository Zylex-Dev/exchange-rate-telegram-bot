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

        # Сохраняем JSON для анализа (опционально)
        with open("exchange_rate_data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

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
                                    buy_rate = rate.get("buy")  # Курс покупки
                                    sell_rate = rate.get("sell")  # Курс продажи
                                    return f"CNY Exchange Rate - Buy: {buy_rate}, Sell: {sell_rate}"
        # else:
        #     # Если data - это словарь, обрабатываем его как раньше
        #     content = data.get("content")
        #     if content:
        #         for item in content:
        #             for rate in item.get("items", []):
        #                 if rate.get("ticker") == "CNY":
        #                     buy_rate = rate.get("buy")  # Курс покупки
        #                     sell_rate = rate.get("sell")  # Курс продажи
        #                     return f"CNY Exchange Rate - Buy: {buy_rate}, Sell: {sell_rate}"

        return "CNY rate not found"
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return "Error fetching exchange rate"


# Тестовая функция main для запуска парсера напрямую
if __name__ == "__main__":
    rate_info = get_cny_exchange_rate()
    print(rate_info)
