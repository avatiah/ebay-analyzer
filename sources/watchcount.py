import os
import base64
import requests

EBAY_API_URL   = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"


def get_oauth_token(client_id: str, client_secret: str) -> str:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
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
        raise RuntimeError(f"Ошибка токена: {resp.status_code} {resp.text[:200]}")
    print(f"    OAuth OK (expires_in: {resp.json().get('expires_in')}s)")
    return resp.json()["access_token"]


def fetch_ebay_data(keyword: str, limit: int = 50) -> list:
    """
    Получает все доступные поля через eBay Browse API.
    Переменные окружения: EBAY_CLIENT_ID, EBAY_CLIENT_SECRET
    """
    client_id     = os.environ.get("EBAY_CLIENT_ID", "")
    client_secret = os.environ.get("EBAY_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print("    ОШИБКА: EBAY_CLIENT_ID / EBAY_CLIENT_SECRET не заданы")
        return []

    token = get_oauth_token(client_id, client_secret)

    # fieldgroups=EXTENDED даёт доп. поля: seller, shipping, condition и др.
    params = {
        "q":           keyword,
        "limit":       min(limit, 200),
        "sort":        "newlyListed",
        "fieldgroups": "EXTENDED",
    }

    print(f"    Browse API: q={keyword!r}, limit={params['limit']}")

    resp = requests.get(
        EBAY_API_URL,
        headers={
            "Authorization":           f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
            "Content-Type":            "application/json",
        },
        params=params,
        timeout=20,
    )
    print(f"    HTTP {resp.status_code}")
    resp.raise_for_status()

    data      = resp.json()
    raw_items = data.get("itemSummaries", [])
    print(f"    Всего на eBay: {data.get('total', '?')}, получено: {len(raw_items)}")

    items = []
    for r in raw_items:
        # ── Цена ─────────────────────────────────────────────────────────
        price_obj    = r.get("price", {})
        price        = price_obj.get("value", "")
        currency     = price_obj.get("currency", "USD")

        # ── Продавец ──────────────────────────────────────────────────────
        seller_obj   = r.get("seller", {})
        seller       = seller_obj.get("username", "")
        fb_score     = str(seller_obj.get("feedbackScore", ""))
        fb_pct       = str(seller_obj.get("feedbackPercentage", ""))

        # ── Доставка ──────────────────────────────────────────────────────
        shipping_options = r.get("shippingOptions", [])
        if shipping_options:
            s = shipping_options[0]
            ship_cost = s.get("shippingCost", {}).get("value", "0")
            ship_type = s.get("shippingServiceCode", s.get("shippingType", ""))
        else:
            ship_cost = ""
            ship_type = ""

        # ── Остальные поля ────────────────────────────────────────────────
        categories   = r.get("categories", [])
        category     = categories[0].get("categoryName", "") if categories else ""

        buying_opts  = r.get("buyingOptions", [])
        buying_opt   = "|".join(buying_opts) if buying_opts else ""

        items.append({
            "item_id":               r.get("itemId", ""),
            "title":                 r.get("title", ""),
            "url":                   r.get("itemWebUrl", ""),
            "image":                 r.get("image", {}).get("imageUrl", ""),
            "price":                 price,
            "currency":              currency,
            "seller":                seller,
            "seller_feedback_score": fb_score,
            "seller_feedback_pct":   fb_pct,
            "condition":             r.get("condition", ""),
            "category":              category,
            "buying_option":         buying_opt,
            "quantity_available":    str(r.get("estimatedAvailabilities", [{}])[0]
                                         .get("estimatedAvailableQuantity", "")),
            "shipping_cost":         ship_cost,
            "shipping_type":         ship_type,
            "listing_end":           r.get("itemEndDate", ""),
            "watchers":              str(r.get("watchCount", "")),
        })

    return items


# Обратная совместимость со старым именем
def fetch_watchcount_data(keyword: str, limit: int = 10) -> list:
    return fetch_ebay_data(keyword, limit)
