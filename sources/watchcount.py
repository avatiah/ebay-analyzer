import random

def fetch_watchcount_data(keyword: str):
    """
    Стабильный мок WatchCount.
    Возвращает 3 товара с ценой и количеством watchers.
    """
    random.seed("wc_" + keyword)

    items = []
    for i in range(3):
        items.append({
            "title": f"{keyword} — вариант #{i+1}",
            "url": f"https://example.com/{keyword.replace(' ', '-')}/{i+1}",
            "price": round(random.uniform(10, 300), 2),
            "currency": "$",
            "watchers": random.randint(0, 150),
        })

    return items
