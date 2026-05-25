import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sources.watchcount import fetch_watchcount_data

# Расширенный заголовок для полноценного конкурентного анализа
CSV_HEADER = [
    "timestamp", "source", "keyword", "title", "url",
    "price", "currency", "watchers", "avg_price", "median_price", 
    "total_results", "seller", "feedback", "trend", "sold", "error"
]


def load_keywords():
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def calc_stats(items: list) -> tuple:
    """Возвращает (avg_price, median_price) для списка товаров."""
    prices = [float(i["price"]) for i in items if i.get("price")]
    if not prices:
        return "", ""
    
    prices.sort()
    avg_price = str(round(sum(prices) / len(prices), 2))
    
    # Расчет медианы для защиты от ценовых выбросов
    n = len(prices)
    if n % 2 == 1:
        median_price = str(round(prices[n // 2], 2))
    else:
        median_price = str(round((prices[n // 2 - 1] + prices[n // 2]) / 2, 2))
        
    return avg_price, median_price


def collect(keyword: str) -> list:
    print(f"\n  Сбор данных для «{keyword}»")
    ts = datetime.datetime.utcnow().isoformat()
    rows = []

    try:
        # Увеличиваем лимит до 50 для репрезентативной выборки рынка
        result_data = fetch_watchcount_data(keyword, limit=50)
        items = result_data.get("items", [])
        total_results = str(result_data.get("total_results", "0"))
    except Exception as e:
        print(f"  WatchCount ошибка: {e}")
        items = []
        total_results = "0"

    avg_price, median_price = calc_stats(items)

    if items:
        for item in items:
            rows.append({
                "timestamp":      ts,
                "source":         "watchcount",
                "keyword":        keyword,
                "title":          item.get("title", ""),
                "url":            item.get("url", ""),
                "price":          item.get("price", ""),
                "currency":       item.get("currency", "USD"),
                "watchers":       item.get("watchers", ""),
                "avg_price":      avg_price,
                "median_price":   median_price,
                "total_results":  total_results,
                "seller":         item.get("seller", ""),
                "feedback":       item.get("feedback", ""),
                "trend":          "",
                "sold":           item.get("sold", ""),
                "error":          ""
            })
    else:
        rows.append({
            "timestamp": ts, "source": "watchcount",
            "keyword": keyword, "title": "", "url": "",
            "price": "", "currency": "", "watchers": "",
            "avg_price": "", "median_price": "", "total_results": total_results,
            "seller": "", "feedback": "", "trend": "", "sold": "",
            "error": "no results"
        })

    return rows


def save_to_csv(rows: list):
    """Дозаписывает данные в конец файла (Append), сохраняя историю трендов."""
    os.makedirs("data", exist_ok=True)
    path = "data/raw_data.csv"
    file_exists = os.path.isfile(path)
    
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"\n  Добавлено {len(rows)} строк → {path}")


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
