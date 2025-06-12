import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_playbill(hall="chamber", pages=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html",
        "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
        "Referer": "https://sales.ft.org.ua/",
        "Cache-Control": "no-cache"
    }
    titles = set()

    for page in range(1, pages + 1):
        url = f"https://sales.ft.org.ua/events?page={page}&hall={hall}"
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("a", class_="performanceCard")

        for card in cards:
            img = card.find("img")
            if img:
                title = img.get("alt", "").strip()
                if title:
                    titles.add(title)

    return sorted(titles)
