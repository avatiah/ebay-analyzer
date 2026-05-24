import requests
from bs4 import BeautifulSoup

def fetch_bidvoy_data(keyword: str) -> dict:
    url = f"https://www.bidvoy.com/{keyword.replace(' ', '_')}/"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    trend = None

    trend_tag = soup.select_one(".trend-value")
    if trend_tag:
        try:
            trend = float(trend_tag.get_text(strip=True).replace("%", "").replace(",", ""))
        except:
            trend = None

    return {
        "trend": trend
    }
