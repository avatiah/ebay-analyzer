import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sources.watchcount import fetch_ebay_data

CSV_HEADER = [
    "timestamp", "keyword",
    "item_id", "title", "url", "image",
    "price", "currency",
    "seller", "seller_feedback_score", "seller_feedback_pct",
    "condition", "category", "buying_option",
    "quantity_available",
    "shipping_cost", "shipping_type",
    "listing_end",
    "watchers",
    "error"
]


def load_keywords():
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def collect(keyword: str) -> list:
    print(f"\n  Сбор данных для «{keyword}»")
    ts = datetime.datetime.utcnow().isoformat()

    try:
        items = fetch_ebay_data(keyword, limit=50)
    except Exception as e:
        print(f"  Ошибка: {e}")
        items = []

    if not items:
        return [{
            "timestamp": ts, "keyword": keyword,
            "item_id": "", "title": "", "url": "", "image": "",
            "price": "", "currency": "",
            "seller": "", "seller_feedback_score": "", "seller_feedback_pct": "",
            "condition": "", "category": "", "buying_option": "",
            "quantity_available": "",
            "shipping_cost": "", "shipping_type": "",
            "listing_end": "", "watchers": "",
            "error": "no results"
        }]

    rows = []
    for item in items:
        rows.append({
            "timestamp":              ts,
            "keyword":                keyword,
            "item_id":                item.get("item_id", ""),
            "title":                  item.get("title", ""),
            "url":                    item.get("url", ""),
            "image":                  item.get("image", ""),
            "price":                  item.get("price", ""),
            "currency":               item.get("currency", "USD"),
            "seller":                 item.get("seller", ""),
            "seller_feedback_score":  item.get("seller_feedback_score", ""),
            "seller_feedback_pct":    item.get("seller_feedback_pct", ""),
            "condition":              item.get("condition", ""),
            "category":               item.get("category", ""),
            "buying_option":          item.get("buying_option", ""),
            "quantity_available":     item.get("quantity_available", ""),
            "shipping_cost":          item.get("shipping_cost", ""),
            "shipping_type":          item.get("shipping_type", ""),
            "listing_end":            item.get("listing_end", ""),
            "watchers":               item.get("watchers", ""),
            "error":                  ""
        })

    print(f"  Собрано строк: {len(rows)}")
    return rows


def save_to_csv(rows: list):
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
