import random

def fetch_checkaflip_data(keyword: str):
    """
    Стабильный мок CheckAFlip.
    Возвращает среднюю цену и количество продаж.
    """
    random.seed("cf_" + keyword)

    return {
        "avg_price": round(random.uniform(20, 250), 2),
        "sold": random.randint(5, 200),
    }
