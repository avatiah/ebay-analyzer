import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sources.watchcount import fetch_watchcount_data

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


def calc_avg(items: list) -> str:
    prices = [float(i["price"]) for i in items if i.get("price")]
    if not prices:
        return ""
    return str(round(sum(prices) / len(prices), 2))


def collect(keyword: str) -> list:
    print(f"\n  Сбор данных для «{keyword}»")
    ts = datetime.datetime.utcnow().isoformat()
    rows = []

    # ── WatchCount ────────────────────────────────────────────────────────
    try:
        items = fetch_watchcount_data(keyword, limit=10)
    except Exception as e:
        print(f"  WatchCount ошибка: {e}")
        items = []

    avg_price = calc_avg(items)

    if items:
        for item in items:
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
                "trend":      "",
                "sold":       item.get("sold", ""),
                "error":      ""
            })
    else:
        rows.append({
            "timestamp": ts, "source": "watchcount",
            "keyword": keyword, "title": "", "url": "",
            "price": "", "currency": "", "watchers": "",
            "avg_price": "", "trend": "", "sold": "",
            "error": "no results"
        })

    return rows


def save_to_csv(rows: list):
    """Перезаписывает CSV полностью — только свежие данные."""
    os.makedirs("data", exist_ok=True)
    path = "data/raw_data.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
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
        all_rows.extend(collect(kw))

    if all_rows:
        save_to_csv(all_rows)
        print("Готово!")


if __name__ == "__main__":
    main()
