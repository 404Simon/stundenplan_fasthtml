import requests
from datetime import date
from bs4 import BeautifulSoup
from models import SpeiseplanDay


def get_speiseplan(date: date) -> list[SpeiseplanDay]:
    params = {
        'func': 'make_spl',
        'locId': 12,
        'date': date.strftime('%Y-%m-%d'),
        'lang': 'de',
        'startThisWeek': '',
        'startNextWeek': ''
    }

    r = requests.post('https://sws2.maxmanager.xyz/inc/ajax-php_konnektor.inc.php', data=params)
    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    speiseplan = []
    for item in soup.find_all('div', class_='row splMeal'):
        title = item.find('span', style='font-size:1.5em').text
        price = item.find('div', style='font-size:1.1em;padding:20px 0').text.strip()
        imgTag = item.find('img', class_='largeFoto hidden hidden-xs')
        img = "https://sws2.maxmanager.xyz/" + imgTag['src'] if imgTag else None
        speiseplan.append(SpeiseplanDay(date, title, price, img))
    return speiseplan

