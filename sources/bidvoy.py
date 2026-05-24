import random

def fetch_bidvoy_data(keyword: str):
    """
    Стабильный мок Bidvoy.
    Возвращает тренд (-30% .. +40%).
    """
    random.seed("bv_" + keyword)

    return {
        "trend": round(random.uniform(-30, 40), 1)
    }
