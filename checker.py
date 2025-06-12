import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")


def fetch_event_ids(pages=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html",
        "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
        "Referer": "https://sales.ft.org.ua/",
        "Cache-Control": "no-cache",
    }
    base_url = "https://sales.ft.org.ua/events"
    event_ids = []

    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}&hall=chamber"
        print(f"📄 Перевіряється сторінка {page}: {url}")
        response = requests.get(url, headers=headers)
        print(f"📦 Статус: {response.status_code} | URL: {response.url}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.find_all("a", class_="performanceCard")

        for card in cards:
            img = card.find("img")
            alt = img.get("alt", "") if img else ""
            href = card.get("href", "")
            print(f"↪️ Подія: {alt} — {href}")
            if "Калігула" in alt and "/events/" in href:
                event_id = href.split("/")[-1]
                if event_id not in event_ids:
                    event_ids.append(event_id)
                    print(f"🔎 Знайдено Калігула: {event_id}")

    print(f"✅ Всього знайдено {len(event_ids)} подій")
    return event_ids


def check_seats(event_id):
    print(f"Перевіряю ID {event_id}...")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://sales.ft.org.ua/events/{event_id}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    seats = soup.select("rect.tooltip-button")
    available = [s.get("data-title", "Без назви") for s in seats if     "occupied" not in s.get("class", [])]

    if available:
        msg = f"🎭 Вільні місця на {event_id}:\n" + "\n".join(f"- {s}" for s in available)
        print(msg)
        send_telegram_message(msg)
    else:
        print("Нічого вільного :(")


def main():
    event_ids = fetch_event_ids()
    if not event_ids:
        print("❗ Нічого не знайдено")
    for eid in event_ids:
        check_seats(eid)


if __name__ == "__main__":
    main()
