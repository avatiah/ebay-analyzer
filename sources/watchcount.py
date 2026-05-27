import os
import base64
import requests

EBAY_BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_TOKEN_URL  = "https://api.ebay.com/identity/v1/oauth2/token"


def get_token(client_id: str, client_secret: str) -> str:
    creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp  = requests.post(
        EBAY_TOKEN_URL,
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/x-www-form-urlencoded"},
        data="grant_type=client_credentials&scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope",
        timeout=15,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Token error {resp.status_code}: {resp.text[:200]}")
    print(f"    OAuth OK (expires_in={resp.json().get('expires_in')}s)")
    return resp.json()["access_token"]


def search(token: str, keyword: str, limit: int = 200, offset: int = 0,
           sort: str = "newlyListed", filters: str = "") -> dict:
    params = {
        "q":           keyword,
        "limit":       min(limit, 200),
        "offset":      offset,
        "sort":        sort,
        "fieldgroups": "EXTENDED",
    }
    if filters:
        params["filter"] = filters

    resp = requests.get(
        EBAY_BROWSE_URL,
        headers={
            "Authorization":           f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
            "Content-Type":            "application/json",
        },
        params=params,
        timeout=25,
    )
    resp.raise_for_status()
    return resp.json()


def extract_item(r: dict) -> dict:
    price_obj   = r.get("price", {})
    seller_obj  = r.get("seller", {})
    ships       = r.get("shippingOptions", [])
    ship        = ships[0] if ships else {}
    cats        = r.get("categories", [])
    avail       = (r.get("estimatedAvailabilities") or [{}])[0]

    ship_cost = ship.get("shippingCost", {}).get("value", "")
    if not ship_cost:
        ship_types = r.get("shippingOptions", [])
        if ship_types:
            ship_cost = "0" if "FREE" in str(ship_types[0]).upper() else ""

    return {
        "item_id":               r.get("itemId", ""),
        "title":                 r.get("title", ""),
        "url":                   r.get("itemWebUrl", ""),
        "image":                 r.get("image", {}).get("imageUrl", ""),
        "price":                 price_obj.get("value", ""),
        "currency":              price_obj.get("currency", "USD"),
        "seller":                seller_obj.get("username", ""),
        "seller_feedback_score": str(seller_obj.get("feedbackScore", "")),
        "seller_feedback_pct":   str(seller_obj.get("feedbackPercentage", "")),
        "condition":             r.get("condition", ""),
        "condition_id":          r.get("conditionId", ""),
        "category":              cats[0].get("categoryName", "") if cats else "",
        "category_id":           cats[0].get("categoryId", "") if cats else "",
        "buying_option":         "|".join(r.get("buyingOptions", [])),
        "quantity_available":    str(avail.get("estimatedAvailableQuantity", "")),
        "quantity_sold":         str(avail.get("estimatedSoldQuantity", "")),
        "shipping_cost":         ship_cost,
        "shipping_type":         ship.get("shippingServiceCode", ship.get("shippingType", "")),
        "free_shipping":         "1" if (ship_cost == "0" or "FREE" in str(ship).upper()) else "0",
        "listing_end":           r.get("itemEndDate", ""),
        "top_rated_seller":      "1" if r.get("topRatedBuyingExperience") else "0",
        "item_location":         r.get("itemLocation", {}).get("country", ""),
        "watchers":              str(r.get("watchCount", "")),
        "thumbnail":             r.get("thumbnailImages", [{}])[0].get("imageUrl", "") if r.get("thumbnailImages") else "",
    }


def fetch_ebay_data(keyword: str, limit: int = 200) -> list:
    client_id     = os.environ.get("EBAY_CLIENT_ID", "")
    client_secret = os.environ.get("EBAY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        print("    ОШИБКА: EBAY_CLIENT_ID / EBAY_CLIENT_SECRET не заданы")
        return []

    token = get_token(client_id, client_secret)

    # Получаем все листинги (до limit)
    all_items = []
    offset    = 0
    batch     = 200

    while len(all_items) < limit:
        to_fetch = min(batch, limit - len(all_items))
        print(f"    Запрос offset={offset}, limit={to_fetch}")
        data     = search(token, keyword, limit=to_fetch, offset=offset)
        raw      = data.get("itemSummaries", [])
        total    = data.get("total", 0)
        print(f"    Всего на eBay: {total}, получено в пакете: {len(raw)}")
        if not raw:
            break
        all_items.extend([extract_item(r) for r in raw])
        offset += len(raw)
        if offset >= total or offset >= limit:
            break

    print(f"    Итого извлечено: {len(all_items)}")
    return all_items


# Обратная совместимость
def fetch_watchcount_data(keyword: str, limit: int = 10) -> list:
    return fetch_ebay_data(keyword, limit)
