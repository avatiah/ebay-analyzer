from typing import List
from models import ProductRecord
from sources.watchcount import WatchCountSource
from storage.csv_storage import save_records_to_csv

KEYWORDS = [
    "iphone 13",
    "lego star wars",
    "pokemon cards",
]

def get_sources():
    return [
        WatchCountSource(),
    ]

def main():
    all_records: List[ProductRecord] = []
    for src in get_sources():
        for kw in KEYWORDS:
            print(f"[{src.name}] Парсим: {kw}")
            try:
                records = src.fetch(kw)
                print(f"Найдено: {len(records)}")
                all_records.extend(records)
            except Exception as e:
                print(f"Ошибка: {e}")

    save_records_to_csv(all_records)

if __name__ == "__main__":
    main()
