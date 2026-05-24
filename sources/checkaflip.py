import requests
from bs4 import BeautifulSoup

def fetch_checkaflip_data(keyword: str) -> dict:
    url = f"https://www.checkaflip.com/search?q={keyword.replace(' ', '+')}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    avg_price = None
    sold = None

    avg_tag = soup.select_one(".avg-price")
    if avg_tag:
        try:
            avg_price = float(avg_tag.get_text(strip=True).replace("$", "").replace(",", ""))
        except:
            avg_price = None

    sold_tag = soup.select_one(".sold-count")
    if sold_tag:
        digits = "".join(ch for ch in sold_tag.get_text(strip=True) if ch.isdigit())
        sold = int(digits) if digits else None

    return {
        "avg_price": avg_price,
        "sold": sold,
    }
