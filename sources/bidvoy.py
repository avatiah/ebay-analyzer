import random

def fetch_bidvoy_data(keyword: str) -> dict:
    """
    Стабильный мок-источник Bidvoy.
    Возвращает тренд в процентах (-30% .. +40%).
    """
    random.seed("bidvoy_" + keyword)

    trend = round(random.uniform(-30, 40), 1)

    return {
        "trend": trend
    }
