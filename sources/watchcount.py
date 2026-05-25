import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.watchcount.com/",
}


def parse_number(text: str) -> str:
    """Извлекает первое число из строки."""
    if not text:
        return ""
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return match.group().replace(",", "") if match else ""


def fetch_watchcount_data(keyword: str, limit: int = 10) -> list:
    """
    Скрапит watchcount.com и возвращает список товаров.
    Каждый элемент: title, url, price, currency, watchers, sold
    """
    url = (
        f"https://www.watchcount.com/live/"
        f"{requests.utils.quote(keyword)}/-/all?site=EBAY_US"
    )
    print(f"    WatchCount GET {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        print(f"    HTTP {resp.status_code}, размер: {len(resp.text)} байт")
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    Ошибка запроса: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    items = []

    # Каждый товар на watchcount.com находится в блоке с классом содержащим данные
    # Структура: таблица или div-блоки с данными о товарах
    # Пробуем несколько селекторов
    rows = (
        soup.select("table.wctable tr.wcrow") or
        soup.select("tr.wcrow") or
        soup.select(".wcitem") or
        soup.select("div.item")
    )
    print(f"    Найдено блоков товаров: {len(rows)}")

    # Если не нашли через классы — ищем через структуру страницы
    if not rows:
        # Ищем все ссылки на ebay внутри результатов
        ebay_links = soup.select('a[href*="ebay.com/itm"]')
        print(f"    Найдено eBay ссылок: {len(ebay_links)}")
        for link in ebay_links[:limit]:
            parent = link.find_parent("td") or link.find_parent("div") or link.find_parent("li")
            if not parent:
                continue
            block_text = parent.get_text(" ", strip=True)

            title = link.get_text(strip=True)
            href  = link.get("href", "")

            # Цена
            price_match = re.search(r"\$\s*([\d,]+\.?\d*)", block_text)
            price = price_match.group(1).replace(",", "") if price_match else ""

            # Watchers
            watch_match = re.search(r"([\d,]+)\s*(?:watch|watcher)", block_text, re.I)
            watchers = watch_match.group(1).replace(",", "") if watch_match else ""

            # Sold
            sold_match = re.search(r"([\d,]+)\s*(?:sold|sale)", block_text, re.I)
            sold = sold_match.group(1).replace(",", "") if sold_match else ""

            if title and href:
                items.append({
                    "title":    title,
                    "url":      href,
                    "price":    price,
                    "currency": "USD",
                    "watchers": watchers,
                    "sold":     sold,
                })
            if len(items) >= limit:
                break

    else:
        for row in rows[:limit]:
            # Заголовок и ссылка
            link_el = row.select_one('a[href*="ebay.com"]') or row.select_one("a")
            title   = link_el.get_text(strip=True) if link_el else ""
            href    = link_el.get("href", "") if link_el else ""

            text = row.get_text(" ", strip=True)

            price_match = re.search(r"\$\s*([\d,]+\.?\d*)", text)
            price = price_match.group(1).replace(",", "") if price_match else ""

            watch_match = re.search(r"([\d,]+)\s*(?:watch|watcher)", text, re.I)
            watchers = watch_match.group(1).replace(",", "") if watch_match else ""

            sold_match = re.search(r"Sold[:\s]*([\d,]+)", text, re.I)
            sold = sold_match.group(1).replace(",", "") if sold_match else ""

            if title:
                items.append({
                    "title":    title,
                    "url":      href,
                    "price":    price,
                    "currency": "USD",
                    "watchers": watchers,
                    "sold":     sold,
                })

    print(f"    Извлечено товаров: {len(items)}")

    # Отладка: если пусто — покажем кусок HTML
    if not items:
        print(f"    HTML (первые 1000 символов):\n{resp.text[:1000]}")

    return items
