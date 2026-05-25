import csv
import datetime
import os
import re
import time

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": "https://www.ebay.com/",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

CSV_HEADER = [
    "timestamp", "source", "keyword", "title", "url",
    "price", "currency", "watchers", "avg_price", "trend", "sold", "error"
]


def load_keywords():
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def parse_price(text):
    """Извлекает первое числовое значение цены из строки."""
    if not text:
        return "", ""
    # Берём первую цену если диапазон (например "10.00 to 20.00")
    match = re.search(r"([\$€£]?)\s*([\d,]+\.?\d*)", text.replace(",", ""))
    if match:
        symbol = match.group(1) or "$"
        value = match.group(2)
        currency_map = {"$": "USD", "€": "EUR", "£": "GBP"}
        return value, currency_map.get(symbol, "USD")
    return "", ""


def scrape(keyword):
    url = f"https://www.ebay.com/sch/i.html?_nkw={requests.utils.quote(keyword)}&_sacat=0&LH_BIN=1&_sop=12"
    print(f"  GET {url}")

    session = requests.Session()
    # Сначала заходим на главную чтобы получить cookies
    try:
        session.get("https://www.ebay.com/", headers=HEADERS, timeout=15)
        time.sleep(1)
    except Exception:
        pass

    try:
        resp = session.get(url, headers=HEADERS, timeout=20)
        print(f"  HTTP {resp.status_code}, размер: {len(resp.text)} байт")
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Ошибка запроса: {e}")
        return []

    # Проверка на блокировку
    if "captcha" in resp.text.lower() or "robot" in resp.text.lower():
        print("  ВНИМАНИЕ: обнаружена капча или блокировка")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select(".s-item")
    print(f"  Найдено элементов .s-item: {len(items)}")

    # Отладка: если нет результатов — покажем кусок HTML
    if not items:
        print(f"  Первые 500 символов HTML: {resp.text[:500]}")

    results = []
    for item in items:
        title_el = item.select_one(".s-item__title")
        price_el = item.select_one(".s-item__price")
        link_el  = item.select_one("a.s-item__link")

        if not (title_el and price_el and link_el):
            continue

        title = title_el.get_text(strip=True)

        # Пропускаем мусорный первый элемент "Shop on eBay"
        if title.lower() in ("shop on ebay", ""):
            continue

        href = link_el.get("href", "")
        # Убираем tracking параметры, оставляем чистый URL
        href = href.split("?")[0] if "?" in href else href

        price_text = price_el.get_text(strip=True)
        price_val, currency = parse_price(price_text)

        # Дополнительные поля
        watchers_el = item.select_one(".s-item__hotness, .s-item__watchcount")
        watchers = watchers_el.get_text(strip=True) if watchers_el else ""

        sold_el = item.select_one(".s-item__quantity-sold")
        sold = sold_el.get_text(strip=True) if sold_el else ""

        results.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "source":    "ebay",
            "keyword":   keyword,
            "title":     title,
            "url":       href,
            "price":     price_val,
            "currency":  currency,
            "watchers":  watchers,
            "avg_price": "",
            "trend":     "",
            "sold":      sold,
            "error":     ""
        })

        if len(results) >= 10:
            break

    # Считаем среднюю цену по выборке
    prices = [float(r["price"]) for r in results if r["price"]]
    if prices:
        avg = round(sum(prices) / len(prices), 2)
        for r in results:
            r["avg_price"] = avg

    print(f"  Извлечено товаров: {len(results)}")
    return results


def save_to_csv(rows):
    os.makedirs("data", exist_ok=True)
    path = "data/raw_data.csv"
    file_exists = os.path.isfile(path) and os.path.getsize(path) > 0

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"  Сохранено строк: {len(rows)} → {path}")


def main():
    keywords = load_keywords()
    if not keywords:
        print("Нет ключевых слов")
        return

    print(f"Ключевые слова: {keywords}")
    all_rows = []

    for i, kw in enumerate(keywords):
        print(f"\n[{i+1}/{len(keywords)}] Скрапинг: «{kw}»")
        results = scrape(kw)

        if results:
            all_rows.extend(results)
        else:
            print(f"  Нет результатов для «{kw}»")
            all_rows.append({
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "source":    "ebay",
                "keyword":   kw,
                "title":     "", "url":      "",
                "price":     "", "currency": "",
                "watchers":  "", "avg_price":"",
                "trend":     "", "sold":     "",
                "error":     "no results"
            })

        # Пауза между запросами чтобы не получить бан
        if i < len(keywords) - 1:
            time.sleep(2)

    if all_rows:
        save_to_csv(all_rows)


if __name__ == "__main__":
    main()
