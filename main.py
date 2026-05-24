import csv
import os
from datetime import datetime

from sources.watchcount import fetch_watchcount_data
from sources.checkaflip import fetch_checkaflip_data
from sources.bidvoy import fetch_bidvoy_data

CSV_PATH = "data/raw_data.csv"
KEYWORDS_FILE = "keywords.txt"


def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return ["iphone 13", "lego star wars", "pokemon cards"]
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def ensure_csv_header():
    exists = os.path.exists(CSV_PATH)
    if not exists:
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if not exists:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "source",
                "keyword",
                "title",
                "url",
                "price",
                "currency",
                "watchers",
                "avg_price",
                "trend",
                "sold",
                "error",
            ])


def append_rows(rows):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


def main():
    ensure_csv_header()
    keywords = load_keywords()
    now = datetime.utcnow().isoformat()

    for kw in keywords:
        # WatchCount
        try:
            wc_items = fetch_watchcount_data(kw)
            wc_rows = []
            for item in wc_items:
                wc_rows.append([
                    now,
                    "watchcount",
                    kw,
                    item.get("title", ""),
                    item.get("url", ""),
                    item.get("price", ""),
                    item.get("currency", ""),
                    item.get("watchers", ""),
                    "",
                    "",
                    "",
                    "",
                ])
            append_rows(wc_rows)
        except Exception as e:
            append_rows([[now, "watchcount", kw, "", "", "", "", "", "", "", "", str(e)]])

        # CheckAFlip
        try:
            cf_data = fetch_checkaflip_data(kw)
            append_rows([[
                now,
                "checkaflip",
                kw,
                "",
                "",
                "",
                "",
                "",
                cf_data.get("avg_price", ""),
                "",
                cf_data.get("sold", ""),
                "",
            ]])
        except Exception as e:
            append_rows([[now, "checkaflip", kw, "", "", "", "", "", "", "", "", str(e)]])

        # Bidvoy
        try:
            bv_data = fetch_bidvoy_data(kw)
            append_rows([[
                now,
                "bidvoy",
                kw,
                "",
                "",
                "",
                "",
                "",
                "",
                bv_data.get("trend", ""),
                "",
                "",
            ]])
        except Exception as e:
            append_rows([[now, "bidvoy", kw, "", "", "", "", "", "", "", "", str(e)]])


if __name__ == "__main__":
    main()
