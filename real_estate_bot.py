import requests
from bs4 import BeautifulSoup
import telegram
import time

# Конфигурация
TOKEN = '7530728296:AAFzKT3N7SXK6BJSAPjn28Bxu9te5-iIaI0'  # Вставь сюда токен, который ты получил от BotFather
CHAT_ID = '716240292'  # Вставь сюда chat_id
bot = telegram.Bot(token=TOKEN)

# URL-ы сайтов с объявлениями
URLS = [
    "https://kazan.cian.ru/snyat/",  # Вставь URL первого сайта
    "https://www.avito.ru/all/kvartiry/sdam/na_dlitelnyy_srok",  # Вставь URL второго сайта
]

# Хранилище уже отправленных объявлений
sent_listings = set()

# Условие по цене
MAX_PRICE = 45000  # Максимальная цена в рублях
CITY = "Казань"    # Город

def parse_site(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = soup.find_all('div', class_='listing')  # Настрой под каждый сайт

    for listing in listings:
        title = listing.find('h2').text
        link = listing.find('a')['href']

        # Полный URL (если ссылка относительная)
        full_link = link if link.startswith("http") else url + link

        # Извлечение цены и города
        price_text = listing.find('div', class_='iva-item-priceStep-TIzu3').text
        city_text = listing.find('div', class_='geo-root-NrkbV').text  # Проверь селектор для города

        # Конвертация цены в число
        try:
            price = int(price_text.replace(" ", "").replace("руб.", ""))
        except ValueError:
            price = MAX_PRICE + 1  # Если цена не распознана, игнорируем объявление

        # Проверяем объявление на наличие слова "собственник", соответствие городу и цене
        if price <= MAX_PRICE and CITY.lower() in city_text.lower() and check_ownership(full_link) and full_link not in sent_listings:
            message = f"Новое объявление: {title} за {price_text} в {city_text}\nСсылка: {full_link}"
            send_telegram_message(message)
            sent_listings.add(full_link)

def check_ownership(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Найди основное текстовое содержание объявления
    description = soup.find('div', class_='description')  # Настрой под сайт
    if description and "собственник" in description.text.lower():
        return True
    return False

def send_telegram_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    while True:
        for url in URLS:
            parse_site(url)
        time.sleep(300)  # Проверка каждые 5 минут

if __name__ == '__main__':
    main()

