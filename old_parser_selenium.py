from selenium import webdriver
from bs4 import BeautifulSoup
import time


# with open("full_page_content.html", "w", encoding="utf-8") as file:
#     file.write(html)
#
# with open("needed_currency_block.html", "w", encoding="utf-8") as file:
#             file.write(str(cny_row))


def get_cny_exchange_rate() -> str:
    # Открытие страницы с Selenium
    url = "https://www.gazprombank.ru/personal/courses/"
    driver = webdriver.Chrome()  # Убедитесь, что драйвер Chrome установлен
    driver.get(url)

    # Подождите, пока данные загрузятся
    time.sleep(5)

    # Получение HTML-кода после загрузки данных
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    try:
        # Найдите нужный элемент с помощью CSS-селекторов или атрибутов
        # Например, курс покупки может находиться в ячейке рядом с названием "CNY"
        currency_row = soup.find_all("div", class_="courses_table__line-40b")

        # Получаем четвертый элемент
        if len(currency_row) >= 4:
            cny_row = currency_row[3]
            buy_rate = cny_row.find_all("span")[-1].text.strip()
            return f"CNY Exchange Rate to buy: {buy_rate} RUB"
        else:
            print("CNY course not found")
    except AttributeError:
        print("Error in the search of CNY course")
