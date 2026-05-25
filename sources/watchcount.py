import requests
import re
import xml.etree.ElementTree as ET

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}


def parse_price(text: str):
    """Извлекает числовое значение цены из строки."""
    if not text:
        return "", "USD"
    sym_map = {"$": "USD", "€": "EUR", "£": "GBP"}
    match = re.search(r"([\$€£])?\s*([\d,]+\.?\d*)", text.replace(",", ""))
    if match:
        sym = match.group(1) or "$"
        val = match.group(2)
        return val, sym_map.get(sym, "USD")
    return "", "USD"


def fetch_watchcount_data(keyword: str, limit: int = 10) -> list:
    """
    Получает товары через eBay RSS-фид — не требует JS, не блокируется.
    URL: https://rss.ebay.com/rss2?satitle=...&sacat=0
    """
    url = (
        f"https://rss.ebay.com/rss2"
        f"?satitle={requests.utils.quote(keyword)}"
        f"&sacat=0&LH_BIN=1&_sop=12"
    )
    print(f"    eBay RSS GET {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        print(f"    HTTP {resp.status_code}, размер: {len(resp.content)} байт")
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    Ошибка запроса: {e}")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        print(f"    Ошибка парсинга XML: {e}")
        print(f"    Ответ (первые 500): {resp.text[:500]}")
        return []

    # RSS namespace для eBay
    ns = {
        "ebay": "urn:ebay:apis:eBLBaseComponents",
    }

    items = []
    channel = root.find("channel")
    if channel is None:
        print("    Нет тега <channel> в RSS")
        return []

    rss_items = channel.findall("item")
    print(f"    Найдено RSS-элементов: {len(rss_items)}")

    for item in rss_items[:limit]:
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link")  or "").strip()

        # Цена из description или специального тега
        description = item.findtext("description") or ""
        price_raw = ""

        # eBay кладёт цену в description как "$XX.XX"
        price_match = re.search(r"([\$€£])\s*([\d,]+\.?\d*)", description)
        if price_match:
            price_raw = price_match.group(1) + price_match.group(2)

        price_val, currency = parse_price(price_raw)

        # Watchers — eBay RSS не даёт watchers, оставляем пустым
        watchers = ""

        # Sold — тоже не в RSS
        sold = ""

        # Убираем мусор из title
        title = re.sub(r"\s+", " ", title).strip()

        # Убираем tracking из URL
        clean_url = link.split("?")[0] if "?" in link else link

        if title and link:
            items.append({
                "title":    title,
                "url":      clean_url,
                "price":    price_val,
                "currency": currency,
                "watchers": watchers,
                "sold":     sold,
            })

    print(f"    Извлечено товаров: {len(items)}")

    if not items:
        print(f"    XML (первые 800):\n{resp.text[:800]}")

    return items
