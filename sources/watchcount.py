import random
from typing import List, Dict

def fetch_watchcount_data(keyword: str) -> List[Dict]:
    """
    Стабильный мок-источник WatchCount.
    Никаких запросов в интернет — только псевдоданные.
    """
    random.seed(keyword)  # детерминированно для одного и того же keyword

    items = []
    for i in range(3):
        price = round(random.uniform(10, 300), 2)
        watchers = random.randint(0, 150)

        items.append({
            "title": f"{keyword} — вариант #{i+1}",
            "url": f"https://example.com/{keyword.replace(' ', '-')}/{i+1}",
            "price": price,
            "currency": "€",
            "watchers": watchers,
        })

    return items
