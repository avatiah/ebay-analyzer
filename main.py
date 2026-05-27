import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sources.watchcount import fetch_ebay_data

CSV_HEADER = [
    "timestamp", "keyword",
    "item_id", "title", "url", "image", "thumbnail",
    "price", "currency",
    "seller", "seller_feedback_score", "seller_feedback_pct", "top_rated_seller",
    "condition", "condition_id",
    "category", "category_id",
    "buying_option",
    "quantity_available", "quantity_sold",
    "shipping_cost", "shipping_type", "free_shipping",
    "listing_end", "item_location", "watchers",
]


def load_keywords():
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def collect(keyword: str) -> list:
    print(f"\n  [{keyword}] Сбор данных...")
    ts = datetime.datetime.utcnow().isoformat()

    try:
        items = fetch_ebay_data(keyword, limit=200)
    except Exception as e:
        print(f"  Ошибка: {e}")
        items = []

    if not items:
        return [{"timestamp": ts, "keyword": keyword, **{k: "" for k in CSV_HEADER if k not in ("timestamp","keyword")}}]

    rows = []
    for item in items:
        row = {"timestamp": ts, "keyword": keyword}
        for key in CSV_HEADER:
            if key not in ("timestamp", "keyword"):
                row[key] = item.get(key, "")
        rows.append(row)

    print(f"  [{keyword}] Собрано: {len(rows)} товаров")
    return rows


def save_csv(rows: list):
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
        print("Нет ключевых слов"); return

    print(f"Ключевые слова: {keywords}")
    all_rows = []
    for kw in keywords:
        all_rows.extend(collect(kw))

    if all_rows:
        save_csv(all_rows)
        print("Готово!")


if __name__ == "__main__":
    main()
