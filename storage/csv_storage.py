import csv
from models import ProductRecord
from datetime import datetime

CSV_PATH = "data/raw_data.csv"

def save_records_to_csv(records):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        timestamp = datetime.utcnow().isoformat()

        for r in records:
            writer.writerow([
                timestamp,
                r.source,
                r.keyword,
                r.title,
                r.url,
                r.price,
                r.currency,
                r.watchers,
                r.sold,
            ])

    print(f"Сохранено {len(records)} строк в {CSV_PATH}")
