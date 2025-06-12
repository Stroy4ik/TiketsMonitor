import json
import requests
import asyncio
from bs4 import BeautifulSoup
import os
import time
from storage import load_subscriptions
from dotenv import load_dotenv
from telegram import Bot
from telegram.request import HTTPXRequest



# Завантаження .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задано!")

bot = Bot(token=BOT_TOKEN, request=HTTPXRequest())
SENT_FILE = "sent.json"

# Загрузка вже оброблених event_id
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        sent = json.load(f)
else:
    sent = {}

subscriptions = load_subscriptions()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
    "Referer": "https://sales.ft.org.ua/",
    "Cache-Control": "no-cache",
}

BASE_URL = "https://sales.ft.org.ua/events"

def find_event_ids_by_title(title, pages=5, halls=["chamber", "main"]):
    ids = []
    for hall in halls:
        for page in range(1, pages + 1):
            url = f"{BASE_URL}?page={page}&hall={hall}"
            print(f"    🌐 {hall}: {url}")
            resp = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all("a", class_="performanceCard")
            for card in cards:
                img = card.find("img")
                alt = img.get("alt", "").strip() if img else ""
                if alt.strip().lower() == title.strip().lower():
                    href = card.get("href", "")
                    if "/events/" in href:
                        event_id = href.split("/")[-1]
                        ids.append(event_id)
    return ids

def check_seats(event_id):
    url = f"https://sales.ft.org.ua/events/{event_id}"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    seats = soup.select("rect.tooltip-button")
    available = [
        s.get("data-title", "Без назви") for s in seats
        if "occupied" not in s.get("class", [])
    ]
    return available

async def send_async_message(uid, msg):
    try:
        await bot.send_message(chat_id=uid, text=msg, parse_mode='HTML')
        print(f"📤 Надіслано користувачу {uid}")
    except Exception as e:
        print(f"❌ Не вдалося надіслати {uid}: {e}")

def notify_users(title, event_id, seats):
    msg = f"🎭 Нова подія '{title}' — <b>{len(seats)} вільних місць</b>!\n"
    msg += f"https://sales.ft.org.ua/events/{event_id}\n\n"
    msg += "(Перевірте доступні місця на сайті)"

    for uid, titles in subscriptions.items():
        if title in titles:
            asyncio.run(send_async_message(uid, msg))

def run_monitor_loop(delay_minutes=1):
    while True:
        print("⏳ Запуск моніторингу...")

        for title in set(t for subs in subscriptions.values() for t in subs):
            print(f"🔎 Перевіряю: {title}")
            event_ids = find_event_ids_by_title(title)
            print(f"  🔍 Знайдено {len(event_ids)} ID: {event_ids}")

            sent.setdefault(title, [])
            new_ids = [eid for eid in event_ids if eid not in sent[title]]
            print(f"  🆕 Нові ID: {new_ids}")

            for eid in new_ids:
                seats = check_seats(eid)
                print(f"    🎫 {eid}: {len(seats)} вільних місць")
                if seats:
                    notify_users(title, eid, seats)
                sent[title].append(eid)

        with open(SENT_FILE, "w", encoding="utf-8") as f:
            json.dump(sent, f, ensure_ascii=False, indent=2)

        print(f"🕒 Очікування {delay_minutes} хв...")
        time.sleep(delay_minutes * 60)

if __name__ == "__main__":
    run_monitor_loop(delay_minutes=1)
