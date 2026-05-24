import random

def fetch_checkaflip_data(keyword: str) -> dict:
    """
    Стабильный мок-источник CheckAFlip.
    Возвращает среднюю цену и количество продаж.
    """
    random.seed("checkaflip_" + keyword)

    avg_price = round(random.uniform(20, 250), 2)
    sold = random.randint(5, 200)

    return {
        "avg_price": avg_price,
        "sold": sold,
    }
