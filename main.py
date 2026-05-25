import csv
import datetime
import os
import sys

# Добавляем sources/ в путь
sys.path.insert(0, os.path.dirname(__file__))

from sources.watchcount import fetch_watchcount_data
from sources.checkaflip import fetch_checkaflip_data
from sources.bidvoy import fetch_bidvoy_data

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


def collect(keyword: str) -> list:
    """Собирает данные из всех источников для одного ключевого слова."""
    print(f"\n  Сбор данных для «{keyword}»")
    rows = []
    ts = datetime.datetime.utcnow().isoformat()

    # ── WatchCount: список товаров ────────────────────────────────────────
    try:
        wc_items = fetch_watchcount_data(keyword)
        print(f"  WatchCount: {len(wc_items)} товаров")
    except Exception as e:
        print(f"  WatchCount ошибка: {e}")
        wc_items = []

    # ── CheckAFlip: средняя цена и продажи ────────────────────────────────
    try:
        cf = fetch_checkaflip_data(keyword)
        avg_price = cf.get("avg_price", "")
        sold_total = cf.get("sold", "")
        print(f"  CheckAFlip: avg_price={avg_price}, sold={sold_total}")
    except Exception as e:
        print(f"  CheckAFlip ошибка: {e}")
        avg_price = ""
        sold_total = ""

    # ── Bidvoy: тренд ─────────────────────────────────────────────────────
    try:
        bv = fetch_bidvoy_data(keyword)
        trend = bv.get("trend", "")
        print(f"  Bidvoy: trend={trend}%")
    except Exception as e:
        print(f"  Bidvoy ошибка: {e}")
        trend = ""

    # ── Собираем строки ───────────────────────────────────────────────────
    if wc_items:
        for item in wc_items:
            rows.append({
                "timestamp":  ts,
                "source":     "watchcount",
                "keyword":    keyword,
                "title":      item.get("title", ""),
                "url":        item.get("url", ""),
                "price":      item.get("price", ""),
                "currency":   item.get("currency", "USD"),
                "watchers":   item.get("watchers", ""),
                "avg_price":  avg_price,
                "trend":      trend,
                "sold":       sold_total,
                "error":      ""
            })
    else:
        rows.append({
            "timestamp":  ts,
            "source":     "watchcount",
            "keyword":    keyword,
            "title":      "", "url":   "",
            "price":      "", "currency": "",
            "watchers":   "",
            "avg_price":  avg_price,
            "trend":      trend,
            "sold":       sold_total,
            "error":      "no items from watchcount"
        })

    return rows


def save_to_csv(rows: list):
    os.makedirs("data", exist_ok=True)
    path = "data/raw_data.csv"
    file_exists = os.path.isfile(path) and os.path.getsize(path) > 0

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"\n  Сохранено {len(rows)} строк → {path}")


def main():
    keywords = load_keywords()
    if not keywords:
        print("Нет ключевых слов")
        return

    print(f"Ключевые слова: {keywords}")
    all_rows = []

    for kw in keywords:
        rows = collect(kw)
        all_rows.extend(rows)

    if all_rows:
        save_to_csv(all_rows)
        print("Готово!")
    else:
        print("Нет данных для сохранения")


if __name__ == "__main__":
    main()
