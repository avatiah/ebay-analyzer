import os
import requests
import base64

EBAY_API_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"


def get_oauth_token(client_id: str, client_secret: str) -> str:
    """Получает OAuth токен через Client Credentials Grant."""
    credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    resp = requests.post(
        EBAY_TOKEN_URL,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=client_credentials&scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope",
        timeout=15,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Ошибка получения токена: {resp.status_code} {resp.text[:200]}")

    token = resp.json().get("access_token")
    print(f"    OAuth токен получен (expires_in: {resp.json().get('expires_in')}s)")
    return token


def fetch_watchcount_data(keyword: str, limit: int = 50) -> dict:
    """
    Получает товары через официальный eBay Browse API, включая данные продавцов.
    """
    client_id     = os.environ.get("EBAY_CLIENT_ID", "")
    client_secret = os.environ.get("EBAY_CLIENT_SECRET", "")

    default_response = {"total_results": 0, "items": []}

    if not client_id or not client_secret:
        print("    ОШИБКА: EBAY_CLIENT_ID или EBAY_CLIENT_SECRET не заданы")
        return default_response

    try:
        token = get_oauth_token(client_id, client_secret)
    except Exception as e:
        print(f"    Ошибка авторизации: {e}")
        return default_response

    params = {
        "q":           keyword,
        "limit":       limit,
        "sort":        "newlyListed",
        "filter":      "buyingOptions:{FIXED_PRICE}",
    }

    print(f"    eBay Browse API: q={keyword}, limit={limit}")

    try:
        resp = requests.get(
            EBAY_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                "Content-Type": "application/json",
            },
            params=params,
            timeout=20,
        )
        print(f"    HTTP {resp.status_code}")
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    Ошибка запроса: {e}")
        return default_response

    data = resp.json()
    raw_items = data.get("itemSummaries", [])
    total_results = data.get("total", 0)
    print(f"    Найдено товаров в базе eBay: {total_results}, получено для анализа: {len(raw_items)}")

    items = []
    for item in raw_items:
        # Цена
        price_obj = item.get("price", {})
        price_val = price_obj.get("value", "")
        currency  = price_obj.get("currency", "USD")

        # Watchers
        watchers = str(item.get("watchCount", ""))

        # Данные продавца (Критично для анализа конкурентов)
        seller_obj = item.get("seller", {})
        seller_name = seller_obj.get("username", "")
        feedback = str(seller_obj.get("feedbackScore", ""))

        # Имитируем объем продаж на основе истории листинга, если доступно
        sold = str(item.get("bidCount", ""))  # Для фиксированных цен можно использовать сторонние маркеры

        items.append({
            "title":    item.get("title", ""),
            "url":      item.get("itemWebUrl", ""),
            "price":    price_val,
            "currency": currency,
            "watchers": watchers,
            "sold":     sold,
            "seller":   seller_name,
            "feedback": feedback
        })

    return {"total_results": total_results, "items": items}
